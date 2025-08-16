import { createStore, type Store } from 'vuex';
import type { InjectionKey } from 'vue';

// Import all store modules (now all TypeScript)
import SettingsModule from './camera_settings';
import ErrorsModule from './errors';
import ComponentsModule from './components';
import GraphicsModule from './graphics';
import ConfigurationsModule from './configurations';
import LogModule from './log';
import AlgorithmsModule from './algorithms';
import ImageSourcesModule from './image_sources';
import CNCModule from './cnc';
import RobotsModule from './robots';
import ProfilometersModule from './profilometers';
import InspectionListModule from './inspection_list';
import ProcessModule from './process';
import MediaModule from './media';
import AuthModule from './auth';
import ItacModule from './itac';
import HelpModule from './help';
import PeripheralsModule from './peripherals';
import CameraCalibration from './camera_calibration';
import StereoCalibration from './stereo_calibration';
import Annotate from './annotation';

// Define root state interface (using any for now during migration)
export interface RootState {
    cameraSettings: any;
    errors: any;
    components: any;
    graphics: any;
    configurations: any;
    log: any;
    algorithms: any;
    imageSources: any;
    cnc: any;
    robots: any;
    profilometers: any;
    inspections: any;
    process: any;
    media: any;
    auth: any;
    itac: any;
    help: any;
    peripherals: any;
    cameraCalibration: any;
    stereoCalibration: any;
    annotate: any;
}

// Define the injection key for typed store
export const key: InjectionKey<Store<RootState>> = Symbol();

// Create the store with all modules
const store = createStore<RootState>({
    modules: {
        cameraSettings: SettingsModule,
        errors: ErrorsModule,
        components: ComponentsModule,
        graphics: GraphicsModule,
        configurations: ConfigurationsModule,
        log: LogModule,
        algorithms: AlgorithmsModule,
        imageSources: ImageSourcesModule,
        cnc: CNCModule,
        robots: RobotsModule,
        profilometers: ProfilometersModule,
        inspections: InspectionListModule,
        process: ProcessModule,
        media: MediaModule,
        auth: AuthModule,
        itac: ItacModule,
        help: HelpModule,
        peripherals: PeripheralsModule,
        cameraCalibration: CameraCalibration,
        stereoCalibration: StereoCalibration,
        annotate: Annotate
    },
    // Disable strict mode to avoid warnings from Fabric.js observables
    strict: false
});

export default store;