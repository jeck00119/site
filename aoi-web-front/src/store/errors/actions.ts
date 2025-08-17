import type { ActionContext } from 'vuex';
import type { ErrorsState, ErrorItem } from './types';

interface RootState {
    [key: string]: any;
}

type ErrorsActionContext = ActionContext<ErrorsState, RootState>;

export default {
    removeError(context: ErrorsActionContext, payload: { errorId: string }): void {
        const id = payload.errorId;
        context.commit('removeError', id);
    },

    addError(context: ErrorsActionContext, payload: ErrorItem): void {
        context.commit('addError', payload);
    },

    clearErrors(context: ErrorsActionContext): void {
        context.commit('clearAllErrors');
    }
};