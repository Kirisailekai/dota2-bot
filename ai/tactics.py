class Tactics:
    def execute(self, action, target, input_sim):
        if action.name == "MOVE":
            input_sim.move_mouse(*target)
            input_sim.right_click()

        elif action.name == "ATTACK":
            input_sim.move_mouse(*target)
            input_sim.right_click()

        elif action.name == "FARM":
            input_sim.move_mouse(*target)
            input_sim.right_click()

        elif action.name == "RETREAT":
            input_sim.move_mouse(*target)
            input_sim.right_click()
