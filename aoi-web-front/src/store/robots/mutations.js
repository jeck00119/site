export default {
    loadUltraArmPorts(state, payload) {
        state.ultraArmPorts = payload;
    },

    loadRobots(state, payload) {
        state.robots = payload;
    },

    loadRobotTypes(state, payload) {
        state.robotTypes = payload;
    },

    resetRobots(state) {
        state.robots = [];
    },

    resetRobotTypes(state) {
        state.robotTypes = [];
    },

    addRobot(state, payload) {
        state.robots.push(payload);
    },

    removeRobot(state, payload) {
        const idx = state.robots.findIndex(robot => robot.uid === payload.uid);
        state.robots.splice(idx, 1);
    },

    updateRobotConnectionID(state, payload) {
        const idx = state.robots.findIndex(robot => robot.uid === payload.uid);
        if(state.robots[idx].type === 'ultraArm') 
        {
            state.robots[idx].port = payload.id;
        }
        else
        {
            state.robots[idx].ip = payload.id;
        }
    },

    updateRobotType(state, payload) {
        const idx = state.robots.findIndex(robot => robot.uid === payload.uid);
        state.robots[idx].type = payload.type;

        if(payload.type === 'ultraArm')
        {
            delete state.robots[idx].ip;
        }
        else
        {
            delete state.robots[idx].port;
        }
    },

    loadCurrentAngles(state, payload) {
        state.currentAngles = payload;
    },

    loadCurrentRobotPositions(state, payload) {
        state.currentRobotPositions = payload;
    },

    deleteRobotPosition(state, payload) {
        const idx = state.currentRobotPositions.findIndex(position => position.uid === payload.uid);
        state.currentRobotPositions.splice(idx, 1);
    },

    updateCurrentPosition(state, payload) {
        const idx = state.currentRobotPositions.findIndex(position => position.uid === payload.positionUid);
        state.currentRobotPositions[idx].speed = payload.speed;
        state.currentRobotPositions[idx].components = payload.components;
        state.currentRobotPositions[idx].name = payload.name;
    }
}