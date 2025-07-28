import {createStore} from 'vuex';

import SettingsModule from './camera_settings/index.js';
import ErrorsModule from './errors/index.js';
import ComponentsModule from './components/index.js';
import GraphicsModule from './graphics/index.js';
import ConfigurationsModule from './configurations/index.js';
import LogModule from './log/index.js';
import AlgorithmsModule from './algorithms/index.js';
import ImageSourcesModule from './image_sources/index.js';
import CNCModule from './cnc/index.js';
import RobotsModule from './robots/index.js';
import ProfilometersModule from './profilometers/index.js';
import InspectionListModule from './inspection_list/index.js';
import ProcessModule from './process/index.js';
import MediaModule from './media/index.js';
import AuthModule from './auth/index.js';
import ItacModule from './itac/index.js';
import HelpModule from './help/index.js';
import PeripheralsModule from './peripherals/index.js';
import CameraCalibration from './camera_calibration/index.js';
import StereoCalibration from './stereo_calibration/index.js';
import Annotate from './annotation/index.js';

const store = createStore({
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
    }
});

export default store;