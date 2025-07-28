import { createApp } from 'vue'

import App from './App.vue'

import CoreUI from "@coreui/vue";
import "@coreui/coreui/dist/css/coreui.css";
import './style.css';

import UUID from 'vue3-uuid';

import { library } from '@fortawesome/fontawesome-svg-core';
import { faPhone, faHouse, faMagnifyingGlassChart, faScrewdriverWrench, faGear, faGears, faUser,
    faQuestion, faClipboardCheck, faCamera, faRepeat, faImage, faTrashCan,
    faSdCard, faPlay, faCubesStacked, faFloppyDisk, faPlus, faTrash, faArrowsRotate, faArrowRotateLeft, 
    faEject, faStop, faArrowRotateRight, faLockOpen, faMinus, faSignature, faFlagCheckered, faNetworkWired, 
    faPlayCircle, faCheck, faX, faVideoCamera, faImages, faExclamationCircle, faArrowRight, faToggleOn, faToggleOff, 
    faFolderOpen, faLocationDot, faMagnifyingGlass, faArrowsUpDownLeftRight, faSun, faCircleHalfStroke, faDroplet,
    faGem, faChartLine, faPlusMinus, faWandMagicSparkles, faCameraRotate, faAnglesRight, faE, faExpand, faArrowsLeftRight, faCrop, faClock, faFileCirclePlus, faCircleInfo  } from '@fortawesome/free-solid-svg-icons';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';

import { OhVueIcon, addIcons } from 'oh-vue-icons';
import { BiPlayCircleFill, IoServerSharp, SiSpeedtest, OiDiffRenamed, SiKdenlive,
    BiCameraVideoFill, MdRepeatoneOutlined, RiSave3Fill, FaFileImport, FaFileExport,
    BiStopFill, FaFileUpload, FaFileDownload, IoAddCircleSharp, MdModeeditoutlineSharp,
    MdDeleteRound, FcDisclaimer, FcUnlock, FcOk, FcCameraAddon, FcCommandLine, FcSupport, FcCancel,
    IoSendSharp, IoRocketSharp, FaRegularSmile, HiEmojiSad, CoMatrix, FaCog, BiExclamationCircleFill, BiTriangleHalf,
    HiSolidQuestionMarkCircle, MdRestartalt, FaServer, MdViewarrayRound, FaExclamationTriangle, FaCopy, FaInfoCircle,
    LaClipboardListSolid, MdSettingsinputcomponent, SiTarget, MdDashboardcustomize, FaListUl, CoCameraControl,
    BiBugFill, FaTrash, ViFileTypeLightJson, OiFileDirectoryOpenFill } from 'oh-vue-icons/icons';

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

library.add(faPhone);
library.add(faHouse);
library.add(faMagnifyingGlassChart);
library.add(faScrewdriverWrench);
library.add(faGear);
library.add(faGears);
library.add(faUser);
library.add(faQuestion);
library.add(faClipboardCheck);
library.add(faCamera);
library.add(faRepeat);
library.add(faImage);
library.add(faNetworkWired);
library.add(faTrashCan);
library.add(faSdCard);
library.add(faPlay);
library.add(faCubesStacked);
library.add(faFloppyDisk);
library.add(faPlus);
library.add(faTrash);
library.add(faArrowsRotate);
library.add(faArrowRotateLeft);
library.add(faArrowRotateRight)
library.add(faLockOpen)
library.add(faStop)
library.add(faMinus)
library.add(faSignature);
library.add(faFlagCheckered);
library.add(faPlayCircle);
library.add(faCheck);
library.add(faX);
library.add(faVideoCamera);
library.add(faImages);
library.add(faExclamationCircle);
library.add(faArrowRight);
library.add(faToggleOn);
library.add(faToggleOff);
library.add(faFolderOpen);
library.add(faMagnifyingGlass);
library.add(faLocationDot);
library.add(faArrowsUpDownLeftRight);
library.add(faSun);
library.add(faCircleHalfStroke);
library.add(faDroplet);
library.add(faGem);
library.add(faChartLine);
library.add(faPlusMinus);
library.add(faWandMagicSparkles);
library.add(faCameraRotate);
library.add(faAnglesRight);
library.add(faExpand);
library.add(faArrowsLeftRight);
library.add(faCrop);
library.add(faClock);
library.add(faFileCirclePlus);
library.add(faCircleInfo);






addIcons(BiPlayCircleFill, IoServerSharp, SiSpeedtest, OiDiffRenamed, SiKdenlive, BiCameraVideoFill,
    MdRepeatoneOutlined, RiSave3Fill, FaFileImport, FaFileExport, BiStopFill, FaFileUpload, FaFileDownload,
    IoAddCircleSharp, MdModeeditoutlineSharp, MdDeleteRound, FcDisclaimer, FcUnlock, FcOk, FcCameraAddon,
    FcCommandLine, FcSupport, FcCancel, IoSendSharp, IoRocketSharp, FaRegularSmile, HiEmojiSad, CoMatrix, FaCog,
    BiExclamationCircleFill, HiSolidQuestionMarkCircle, MdRestartalt, FaServer, MdViewarrayRound, FaExclamationTriangle,
    FaCopy, FaInfoCircle, LaClipboardListSolid, MdSettingsinputcomponent, SiTarget, MdDashboardcustomize,
    FaListUl, CoCameraControl, BiBugFill, FaTrash, ViFileTypeLightJson, OiFileDirectoryOpenFill);

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


