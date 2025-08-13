import type { ErrorsState, ErrorItem } from './types';

export default {
    getErrors(state: ErrorsState): ErrorItem[] {
        return state.errors;
    },

    isEmpty(state: ErrorsState): boolean {
        return state.errors.length === 0;
    },

    numberOfErrors(state: ErrorsState): number {
        return state.errors.length;
    }
};