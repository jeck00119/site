import type { Module } from 'vuex';
import type { ErrorsState } from './types';

interface RootState {
    [key: string]: any;
}
import getters from './getters';
import mutations from './mutations';
import actions from './actions';

const errorsModule: Module<ErrorsState, RootState> = {
    namespaced: true,
    state: (): ErrorsState => ({
        errors: []
    }),
    getters,
    mutations,
    actions
};

export default errorsModule;