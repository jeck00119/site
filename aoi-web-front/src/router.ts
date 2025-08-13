import { createRouter, createWebHistory, type Router, type RouteRecordRaw } from 'vue-router';
import { useRouteGuards } from './composables/useRouter';

// Convert all imports to lazy loading for better code splitting
const HomeComponent = () => import('./components/pages/home/HomeComponent.vue');
const ResultsList = () => import('./components/pages/home/ResultsList.vue');

const UserSignup = () => import('./components/pages/auth/UserSignup.vue');
const UserLogin = () => import('./components/pages/auth/UserLogin.vue');

const Configurations = () => import('./components/configurations/Configurations.vue');

import store from './store/index.js';
import type { Store } from 'vuex';

const ComponentsConfiguration = () => import('./components/pages/inspections/ComponentsConfiguration.vue');
const CustomComponentsConfiguration = () => import('./components/pages/inspections/CustomComponentsConfiguration.vue');
const IdentificationConfiguration = () => import('./components/pages/inspections/IdentificationConfiguration.vue');
const InspectionList = () => import('./components/pages/inspections/InspectionList.vue');
const ReferencesConfiguration = () => import('./components/pages/inspections/ReferencesConfiguration.vue');

const SystemSettings = () => import('./components/pages/settings/SystemSettings.vue');
const ItacSettings = () => import('./components/itac/ItacSettings.vue');
const ImageSources = () => import('./components/pages/settings/ImageSources.vue');
const CameraCalibration = () => import('./components/pages/settings/CameraCalibration.vue');
const StereoCalibration = () => import('./components/pages/settings/StereoCalibration.vue');

const CNCMachine = () => import('./components/pages/tools/CNCMachine.vue');
const AlgorithmDebug = () => import('./components/pages/tools/AlgorithmDebug.vue');
const LogList = () => import('./components/pages/tools/LogList.vue');
const Media = () => import('./components/pages/tools/Media.vue');
const RobotControl = () => import('./components/pages/tools/RobotControl.vue');
const AutoAnnotate = () => import('./components/pages/tools/AutoAnnotate.vue');

const UserRoles = () => import('./components/pages/auth/UserRoles.vue');

const HelpComponent = () => import('./components/pages/about/HelpComponent.vue');

const routes: RouteRecordRaw[] = [
    {
        path: '/',
        redirect: (to) => {
            // This will be handled by the auth guard instead of hardcoding login redirect
            return '/configurations';
        }
    },
    {
        path: '/aoi', component: HomeComponent
    },
    {
        path: '/inspections-and-results', component: ResultsList
    },
    {
        path: '/components', component: ComponentsConfiguration, meta: { requiresAuth: true }
    },
    {
        path: '/identification', component: IdentificationConfiguration, meta: { requiresAuth: true }
    },
    {
        path: '/references', component: ReferencesConfiguration, meta: { requiresAuth: true }
    },
    {
        path: '/custom-components', component: CustomComponentsConfiguration, meta: { requiresAuth: true }
    },
    {
        path: '/inspection-list', component: InspectionList, meta: { requiresAuth: true }
    },
    {
        path: '/system-settings', component: SystemSettings, meta: { requiresAuth: true }
    },
    {
        path: '/itac-settings', component: ItacSettings, meta: { requiresAuth: true }
    },
    {
        path: '/image-sources', component: ImageSources, meta: { requiresAuth: true }
    },
    {
        path: '/camera-calibration', component: CameraCalibration, meta: { requiresAuth: true }
    },
    {
        path: '/stereo-calibration', component: StereoCalibration, meta: { requiresAuth: true }
    },
    {
        path: '/cnc-machine', component: CNCMachine, meta: { requiresAuth: true }
    },
    {
        path: '/robot-control', component: RobotControl, meta: { requiresAuth: true }
    },
    {
        path: '/auto-annotate', component: AutoAnnotate, meta: { requiresAuth: true }
    },
    {
        path: '/algorithm-debug', component: AlgorithmDebug
    },
    {
        path: '/log', component: LogList, meta: { requiresAuth: true }
    },
    {
        path: '/media', component: Media, meta: { requiresAuth: true }
    },
    {
        path: '/signup', component: UserSignup, meta: { requiresUnauth: true }
    },
    {
        path: '/login', component: UserLogin, meta: { requiresUnauth: true }
    },
    {
        path: '/roles', component: UserRoles, meta: { requiresAdmin: true, requiresAuth: true }
    },
    {
        path: '/help', component: HelpComponent
    },
    {
        path: '/configurations', component: Configurations, meta: { requiresAuth: true }
    }
];

const router: Router = createRouter({
    history: createWebHistory(),
    routes
});

// Enable route guards for authentication
const { authGuard } = useRouteGuards();
router.beforeEach(authGuard);

export default router;
export type { Router };