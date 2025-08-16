import { uuid } from "vue3-uuid";
import { get, post, remove, put } from "../../utils/requests";
import { ipAddress, port } from "../../url";

export default {
    async loadUltraArmPorts(context, _) {
        const { response, responseData } = await get(`http://${ipAddress}:${port}/robot/ultra_arm_ports`);

        if(!response.ok)
        {
            const error = new Error(responseData.detail || `Failed to fetch the available ports!`);
            throw error;
        }
        else
        {
            context.commit('loadUltraArmPorts', responseData);
        }
    },

    async loadRobots(context) {
        const { response, responseData } = await get(`http://${ipAddress}:${port}/robot`);

        if(!response.ok)
        {
            const error = new Error(responseData.detail || `Failed to fetch robots!`);
            throw error;
        }
        else
        {
            context.commit('loadRobots', responseData);
        }
    },

    async loadRobotTypes(context) {
        const { response, responseData } = await get(`http://${ipAddress}:${port}/robot/robot_types`);

        if(!response.ok)
        {
            const error = new Error(responseData.detail || `Failed to fetch robot types!`);
            throw error;
        }
        else
        {
            context.commit('loadRobotTypes', responseData);
        }
    },

    resetRobots(context) {
        context.commit('resetRobots');
    },

    resetRobotTypes(context) {
        context.commit('resetRobotTypes');
    },

    addRobot(context, payload) {
        const robot = {
            uid: uuid.v4(),
            name: payload.name,
            type: payload.type,
            ip: payload.ip
        };

        context.commit('addRobot', robot);
    },

    removeRobot(context, payload) {
        context.commit('removeRobot', payload);
    },

    async saveRobots(context) {
        const robots = context.getters.getRobots;
        const token = context.rootGetters["auth/getToken"] || sessionStorage.getItem('auth-token');

        const response = await post(`http://${ipAddress}:${port}/robot/save`, robots, {
            'content-type': 'application/json',
            'Authorization': token
        });

        if(!response.ok)
        {
            const error = new Error(`Failed to save robots!`);
            throw error;
        }
    },

    updateRobotConnectionID(context, payload) {
        context.commit('updateRobotConnectionID', payload);
    },

    updateRobotType(context, payload) {
        context.commit('updateRobotType', payload);
    },

    async loadCurrentAngles(context, payload) {
        const token = context.rootGetters["auth/getToken"] || sessionStorage.getItem('auth-token');

        const { response, responseData } = await get(`http://${ipAddress}:${port}/robot/${payload.uid}/current_angles`, {
            'content-type': 'application/json',
            'Authorization': token
        });

        if(!response.ok)
        {
            const error = new Error(responseData.detail || `Failed to fetch current angles!`);
            throw error;
        }
        else
        {
            context.commit('loadCurrentAngles', responseData);
        }
    },

    async loadCurrentRobotPositions(context, payload) {
        const token = context.rootGetters["auth/getToken"] || sessionStorage.getItem('auth-token');

        const { response, responseData } = await get(`http://${ipAddress}:${port}/robot/${payload.uid}/positions`, {
            'content-type': 'application/json',
            'Authorization': token
        });

        if(!response.ok)
        {
            const error = new Error(responseData.detail || `Failed to fetch current robot positions!`);
            throw error;
        }
        else
        {
            context.commit('loadCurrentRobotPositions', responseData);
        }
    },

    async deleteRobotPosition(context, payload) {
        const token = context.rootGetters["auth/getToken"] || sessionStorage.getItem('auth-token');

        const response = await remove(`http://${ipAddress}:${port}/robot/${payload.uid}/delete_position`, {
            'content-type': 'application/json',
            'Authorization': token
        });

        if(!response.ok)
        {
            const error = new Error(`Failed to delete position ${payload.uid}!`);
            throw error;
        }
        else
        {
            context.commit('deleteRobotPosition', payload);
        }
    },

    async moveRobotToPosition(context, payload) {
        const token = context.rootGetters["auth/getToken"] || sessionStorage.getItem('auth-token');

        const response = await post(`http://${ipAddress}:${port}/robot/${payload.robotUid}/${payload.positionUid}/move_to_position`, null, {
            'content-type': 'application/json',
            'Authorization': token
        });

        if(!response.ok)
        {
            const error = new Error(`Failed to move robot ${payload.robotUid} to position ${payload.positionUid}!`);
            throw error;
        }
    },

    async moveRobotHome(context, payload) {
        const token = context.rootGetters["auth/getToken"] || sessionStorage.getItem('auth-token');

        const response = await post(`http://${ipAddress}:${port}/robot/${payload.uid}/home`, null, {
            'content-type': 'application/json',
            'Authorization': token
        });

        if(!response.ok)
        {
            const error = new Error(`Failed to home robot ${payload.uid}!`);
            throw error;
        }
    },

    async setRobotJointAngle(context, payload) {
        const token = context.rootGetters["auth/getToken"] || sessionStorage.getItem('auth-token');

        const response = await post(`http://${ipAddress}:${port}/robot/${payload.uid}/set_angle`, {
            joint_number: payload.jointNumber,
            angle: payload.angle,
            speed: payload.speed
        }, {
            'content-type': 'application/json',
            'Authorization': token
        });

        if(!response.ok)
        {
            const error = new Error(`Failed to move robot ${payload.uid} to pose!`);
            throw error;
        }
    },

    async saveCurrentPosition(context, payload) {
        const token = context.rootGetters["auth/getToken"] || sessionStorage.getItem('auth-token');

        const response = await post(`http://${ipAddress}:${port}/robot/${payload.uid}/save_position`, {
            uid: uuid.v4(),
            speed: payload.speed,
            components: payload.components,
            name: payload.name
        }, {
            'content-type': 'application/json',
            'Authorization': token
        });

        if(!response.ok)
        {
            const error = new Error(`Failed to save position for robot ${payload.uid}!`);
            throw error;
        }
    },

    async updateCurrentPosition(context, payload) {
        const token = context.rootGetters["auth/getToken"] || sessionStorage.getItem('auth-token');

        const response = await put(`http://${ipAddress}:${port}/robot/${payload.robotUid}/update_position`, {
            uid: payload.positionUid,
            robot_uid: payload.robotUid,
            speed: payload.speed,
            components: payload.components,
            name: payload.name,
            angles: []
        }, {
            'content-type': 'application/json',
            'Authorization': token
        });

        if(!response.ok)
        {
            const error = new Error(`Failed to update position for robot ${payload.uid}!`);
            throw error;
        }
        else
        {
            context.commit('updateCurrentPosition', payload);
        }
    },

    async releaseServos(context, payload) {
        const token = context.rootGetters["auth/getToken"] || sessionStorage.getItem('auth-token');

        const response = await post(`http://${ipAddress}:${port}/robot/${payload.uid}/release_servos`, null, {
            'content-type': 'application/json',
            'Authorization': token
        });

        if(!response.ok)
        {
            const error = new Error(`Failed to release servos for robot ${payload.uid}!`);
            throw error;
        }
    },

    async powerServos(context, payload) {
        const token = context.rootGetters["auth/getToken"] || sessionStorage.getItem('auth-token');

        const response = await post(`http://${ipAddress}:${port}/robot/${payload.uid}/power_servos`, null, {
            'content-type': 'application/json',
            'Authorization': token
        });

        if(!response.ok)
        {
            const error = new Error(`Failed to power servos for robot ${payload.uid}!`);
            throw error;
        }
    }
}