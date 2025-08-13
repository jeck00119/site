export default {
    getRobots(state) {
        return state.robots;
    },

    getRobotTypes(state) {
        return state.robotTypes;
    },

    getUltraArmPorts(state) {
        return state.ultraArmPorts;
    },

    getCurrentAngles(state) {
        return state.currentAngles;
    },

    getCurrentRobotPositions(state) {
        return state.currentRobotPositions;
    }
}