#include <memory>
#include <rclcpp/rclcpp.hpp>
#include <moveit/move_group_interface/move_group_interface.hpp>
#include <geometry_msgs/msg/pose.hpp>
#include <moveit_msgs/msg/move_it_error_codes.hpp>

using std::placeholders::_1;

std::string channel_to_sub = "/ik_cmd_pub";
std::string group_name = "robotic_arm";

class PsSub : public rclcpp::Node
{
public:
	PsSub() : Node("ps_subscriber")
	{
		// Subscribe to /ee_pose topic
		subscription_ = this->create_subscription<geometry_msgs::msg::Pose>(
			channel_to_sub, 10, std::bind(&PsSub::topic_callback, this, _1));

		RCLCPP_INFO(this->get_logger(), "Subscribed to %s ",channel_to_sub.c_str());

		// Create a timer to initialize MoveGroupInterface after construction
		init_timer_ = this->create_wall_timer(
			std::chrono::milliseconds(100),
			std::bind(&PsSub::initialize_move_group, this));
	}

private:
	void initialize_move_group()
	{
		try
		{
			RCLCPP_INFO(this->get_logger(), "Node namespace: %s", this->get_namespace());

			move_group_interface_ = std::make_shared<moveit::planning_interface::MoveGroupInterface>(
				shared_from_this(), group_name);

			// Motion strictness and predictability
			move_group_interface_->setGoalTolerance(0.001);
			move_group_interface_->setGoalOrientationTolerance(0.001);
			move_group_interface_->setGoalJointTolerance(0.001);
			move_group_interface_->setPlanningTime(1.0);
			move_group_interface_->setNumPlanningAttempts(2);
			move_group_interface_->setPoseReferenceFrame("base_link");
			move_group_interface_->setEndEffectorLink("tool_link");
			move_group_interface_->setMaxVelocityScalingFactor(1.0);
			move_group_interface_->setMaxAccelerationScalingFactor(1.0);

			RCLCPP_INFO(this->get_logger(), "MoveGroupInterface initialized for group: %s", group_name.c_str());
			init_timer_->cancel();
		}
		catch (const std::exception &e)
		{
			RCLCPP_ERROR(this->get_logger(), "Failed to initialize MoveGroupInterface: %s", e.what());
		}
	}


	void topic_callback(const geometry_msgs::msg::Pose::SharedPtr pose)
	{
		// Log the received pose
		RCLCPP_INFO(
			this->get_logger(),
			"Pose: position(x=%.3f, y=%.3f, z=%.3f), Orientation(x=%.3f, y=%.3f, z=%.3f, w=%.3f)",
			pose->position.x, pose->position.y, pose->position.z,
			pose->orientation.x, pose->orientation.y, pose->orientation.z, pose->orientation.w
		);

		// Check if MoveGroupInterface is initialized
		if (!move_group_interface_)
		{
			RCLCPP_ERROR(this->get_logger(), "MoveGroupInterface not initialized! Skipping planning.");
			return;
		}

		try
		{	

			// CARTESIAN PATH PLANNING

			std::vector<geometry_msgs::msg::Pose> waypoints;
			waypoints.push_back(*pose);

			// Set Cartesian path parameters
			double eef_step = 0.01;
			// double jump_threshold = 0.2;
			moveit_msgs::msg::RobotTrajectory trajectory;
			
			// Compute Cartesian Path
			double fraction = move_group_interface_->computeCartesianPath(
				waypoints,
				eef_step,
				// jump_threshold,
				trajectory
			);

			RCLCPP_INFO(this->get_logger(), "Cartesian path fraction: %.2f", fraction);

			if (fraction > 0.80 )
			{
				// Execute
				move_group_interface_->execute(trajectory);
				RCLCPP_INFO(this->get_logger(), "Cartesian path executed successfully");
			}
			else {
				
				// Set the target pose
				move_group_interface_->setPoseTarget(*pose);
				RCLCPP_INFO(this->get_logger(), "Set pose target");

				// Plan
				moveit::planning_interface::MoveGroupInterface::Plan plan_msg;
				bool success = (move_group_interface_->plan(plan_msg) == moveit_msgs::msg::MoveItErrorCodes::SUCCESS);
				RCLCPP_INFO(this->get_logger(), "Planning %s", success ? "succeeded" : "failed");

				if (success)
				{
					// Execute the plan
					move_group_interface_->setStartStateToCurrentState();
					move_group_interface_->execute(plan_msg);
					RCLCPP_INFO(this->get_logger(), "Plan executed successfully");
				}
				else
				{
					RCLCPP_ERROR(this->get_logger(), "Planning failed!");
				}
			}

		}
		catch (const std::exception& e)
		{
			RCLCPP_ERROR(this->get_logger(), "Exception during planning/execution: %s", e.what());
		}
	}

	rclcpp::Subscription<geometry_msgs::msg::Pose>::SharedPtr subscription_;
	std::shared_ptr<moveit::planning_interface::MoveGroupInterface> move_group_interface_;
	rclcpp::TimerBase::SharedPtr init_timer_;
};

int main(int argc, char *argv[])
{	
	rclcpp::init(argc, argv);
	auto node = std::make_shared<PsSub>();
	rclcpp::spin(node);
	rclcpp::shutdown();
	return 0;
}