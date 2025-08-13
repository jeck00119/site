import type { ErrorsState, ErrorItem } from './types';

export default {
    removeError(state: ErrorsState, id: string): void {
        const errorIndex = state.errors.findIndex(error => error.id === id);
        if (errorIndex !== -1) {
            state.errors.splice(errorIndex, 1);
        }
    },

    addError(state: ErrorsState, payload: ErrorItem): void {
        state.errors.push(payload);
    }
};