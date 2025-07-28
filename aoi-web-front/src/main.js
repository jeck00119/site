import { createApp } from 'vue'

import App from './App.vue'

import CoreUI from "@coreui/vue";
import "@coreui/coreui/dist/css/coreui.css";
import './style.css';

import UUID from 'vue3-uuid';

import { library } from '@fortawesome/fontawesome-svg-core';
// All actually used icons - verified from codebase usage
import { faHouse, faMagnifyingGlassChart, faScrewdriverWrench, faGear, faGears, faUser,
    faClipboardCheck, faCamera, faPlay, faStop, faPlus, faTrash, faCheck, faX,
    faExclamationCircle, faCircleInfo, faImages, faFloppyDisk, faVideoCamera, faMinus,
    faTrashCan, faToggleOn, faToggleOff, faFileCirclePlus, faFolderOpen, faMagnifyingGlass,
    faLocationDot, faClock, faArrowsUpDownLeftRight, faSun, faCircleHalfStroke, faDroplet,
    faGem, faChartLine, faPlusMinus, faWandMagicSparkles, faCameraRotate, faArrowsLeftRight,
    faExpand, faCrop, faSignature, faFlagCheckered, faNetworkWired, faPlayCircle, faImage,
    faSdCard, faArrowsRotate, faArrowRotateLeft, faArrowRotateRight, faLockOpen, faCubesStacked } from '@fortawesome/free-solid-svg-icons';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';

import { OhVueIcon, addIcons } from 'oh-vue-icons';
// All actually used OhVueIcons - verified from codebase usage
import { BiPlayCircleFill, IoServerSharp, SiSpeedtest, OiDiffRenamed, SiKdenlive,
    BiCameraVideoFill, MdRepeatoneOutlined, RiSave3Fill, FaFileImport, FaFileExport,
    BiStopFill, FaFileUpload, FaFileDownload, IoAddCircleSharp, MdModeeditoutlineSharp,
    MdDeleteRound, FcDisclaimer, FcUnlock, FcOk, FcCameraAddon, FcCommandLine, FcSupport, 
    FcCancel, IoSendSharp, FaServer, MdRestartalt, CoMatrix, MdViewarrayRound,
    FaExclamationTriangle, FaCopy, LaClipboardListSolid, MdSettingsinputcomponent,
    SiTarget, MdDashboardcustomize, FaListUl, CoCameraControl, BiBugFill, FaTrash,
    ViFileTypeLightJson, OiFileDirectoryOpenFill, BiExclamationCircleFill,
    HiSolidQuestionMarkCircle, FaCog } from 'oh-vue-icons/icons';

import ContextMenu from '@imengyu/vue3-context-menu'
import '@imengyu/vue3-context-menu/lib/vue3-context-menu.css'

import store from './store/index.js';
import router from './router.js';

import BaseSlider from './components/base/BaseSlider.vue';
import BaseIntegerInputBox from './components/base/BaseIntegerInputBox.vue';
import BaseColorPicker from './components/base/BaseColorPicker.vue';
import BaseTextInput from './components/base/BaseTextInput.vue';
import BaseActionButton from './components/base/BaseActionButton.vue';
import BaseButtonRectangle from './components/base/BaseButtonRectangle.vue';
import BaseDropdown from './components/base/BaseDropdown.vue';
import BaseDialog from './components/base/BaseDialog.vue';
import BaseButton from './components/base/BaseButton.vue';
import BaseCard from './components/base/BaseCard.vue';
import BaseCheckbox from './components/base/BaseCheckbox.vue';
import BaseSpinner from './components/base/BaseSpinner.vue';
import BaseTabsWrapper from './components/base/BaseTabsWrapper.vue';
import BaseConfirmation from './components/base/BaseConfirmation.vue';
import BaseTab from './components/base/BaseTab.vue';
import BaseNotification from './components/base/BaseNotification.vue';
import BaseFileLoader from './components/base/BaseFileLoader.vue';


const app = createApp(App);

// Global error handler for better error tracking and user experience
app.config.errorHandler = (err, instance, info) => {
    // Log error details for debugging
    console.error('🚨 Global Vue Error:', {
        error: err,
        component: instance?.$options?.name || 'Unknown Component',
        errorInfo: info,
        timestamp: new Date().toISOString()
    });
    
    // In production, you would send this to an error tracking service like Sentry
    // Example: Sentry.captureException(err, { extra: { info, component: instance?.$options?.name } });
    
    // Show user-friendly notification
    if (instance && instance.$store) {
        instance.$store.dispatch('errors/addError', {
            message: 'An unexpected error occurred. Please try refreshing the page.',
            type: 'error',
            timestamp: Date.now()
        });
    }
};

// Add all actually used icons
library.add(faHouse);
library.add(faMagnifyingGlassChart);
library.add(faScrewdriverWrench);
library.add(faGear);
library.add(faGears);
library.add(faUser);
library.add(faClipboardCheck);
library.add(faCamera);
library.add(faPlay);
library.add(faStop);
library.add(faPlus);
library.add(faTrash);
library.add(faCheck);
library.add(faX);
library.add(faExclamationCircle);
library.add(faCircleInfo);
library.add(faImages);
library.add(faFloppyDisk);
library.add(faVideoCamera);
library.add(faMinus);
library.add(faTrashCan);
library.add(faToggleOn);
library.add(faToggleOff);
library.add(faFileCirclePlus);
library.add(faFolderOpen);
library.add(faMagnifyingGlass);
library.add(faLocationDot);
library.add(faClock);
library.add(faArrowsUpDownLeftRight);
library.add(faSun);
library.add(faCircleHalfStroke);
library.add(faDroplet);
library.add(faGem);
library.add(faChartLine);
library.add(faPlusMinus);
library.add(faWandMagicSparkles);
library.add(faCameraRotate);
library.add(faArrowsLeftRight);
library.add(faExpand);
library.add(faCrop);
library.add(faSignature);
library.add(faFlagCheckered);
library.add(faNetworkWired);
library.add(faPlayCircle);
library.add(faImage);
library.add(faSdCard);
library.add(faArrowsRotate);
library.add(faArrowRotateLeft);
library.add(faArrowRotateRight);
library.add(faLockOpen);
library.add(faCubesStacked);






// Add all actually used OhVueIcons
addIcons(BiPlayCircleFill, IoServerSharp, SiSpeedtest, OiDiffRenamed, SiKdenlive,
    BiCameraVideoFill, MdRepeatoneOutlined, RiSave3Fill, FaFileImport, FaFileExport,
    BiStopFill, FaFileUpload, FaFileDownload, IoAddCircleSharp, MdModeeditoutlineSharp,
    MdDeleteRound, FcDisclaimer, FcUnlock, FcOk, FcCameraAddon, FcCommandLine, FcSupport,
    FcCancel, IoSendSharp, FaServer, MdRestartalt, CoMatrix, MdViewarrayRound,
    FaExclamationTriangle, FaCopy, LaClipboardListSolid, MdSettingsinputcomponent,
    SiTarget, MdDashboardcustomize, FaListUl, CoCameraControl, BiBugFill, FaTrash,
    ViFileTypeLightJson, OiFileDirectoryOpenFill, BiExclamationCircleFill,
    HiSolidQuestionMarkCircle, FaCog);

app.component('base-slider', BaseSlider);
app.component('base-integer-input', BaseIntegerInputBox);
app.component('base-text-input', BaseTextInput);
app.component('base-color-picker', BaseColorPicker);
app.component('base-action-button', BaseActionButton);
app.component('base-button-rectangle', BaseButtonRectangle);
app.component('base-dropdown', BaseDropdown);
app.component('base-dialog', BaseDialog);
app.component('base-button', BaseButton);
app.component('base-card', BaseCard);
app.component('base-checkbox', BaseCheckbox);
app.component('base-spinner', BaseSpinner);
app.component('base-tabs-wrapper', BaseTabsWrapper);
app.component('base-tab', BaseTab);
app.component('base-notification', BaseNotification);
app.component('base-confirmation', BaseConfirmation);
app.component('base-file-loader', BaseFileLoader);
app.component('font-awesome-icon', FontAwesomeIcon);
app.component('v-icon', OhVueIcon);

app.use(store);
app.use(router);
app.use(UUID);
app.use(ContextMenu);

app.use(CoreUI);
app.mount('#app');


