<template>
    <div class="flex-container">
        <div class="title">
            <h1>Inspection List</h1>
        </div>
        <div class="content-wrapper">
            <div class="actions">
                <base-button-rectangle @state-changed="showTableDialog" :disabled="!currentConfiguration || columnNames.length !== 0">
                    <div class="button-container">
                        <div class="button-icon">
                            <v-icon name="io-add-circle-sharp" scale="1.5"/>
                        </div>
                        <div class="button-text">Create Table</div>
                    </div>
                </base-button-rectangle>
                <base-button-rectangle @state-changed="toggleUploadVisibility" :disabled="!currentConfiguration">
                    <div class="button-container">
                        <div class="button-icon">
                            <v-icon name="fa-file-upload" scale="1.5"/>
                        </div>
                        <div class="button-text">Upload</div>
                    </div>
                </base-button-rectangle>
                <base-button-rectangle @state-changed="exportInspectionList" :disabled="!currentConfiguration">
                    <div class="button-container">
                        <div class="button-icon">
                            <v-icon name="fa-file-download" scale="1.5"/>
                        </div>
                        <div class="button-text">Export</div>
                    </div>
                </base-button-rectangle>
                <div class="upload">
                    <upload-inspection-list
                        :show="showUpload"
                        @file-changed="onInspectionListUploaded"
                    ></upload-inspection-list>
                </div>
            </div>
            <div class="table-wrapper">
                <table class="inspections-table" ref="inspectionTable">
                    <thead>
                        <tr>
                            <th
                                v-for="column, idx in columnNames"
                                @click="selectColumn(idx)"
                                @dblclick="showColumnDialogForEdit(idx)"
                                :class="{'selected-column': selectedColumn === idx}"
                            >{{column}}</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="(inspection, idx) in inspections" :key="inspection.uid || idx" v-memo="[inspection, selectedRow === idx, editable]" @click="selectRow(idx)" :class="{'selected-row': selectedRow === idx && !editable}">
                            <td v-for="column, colIdx in columnNames" :key="column">
                                <div v-if="columnTypes[colIdx] === 'Boolean'">
                                    <base-dropdown
                                        :current="inspection[column]"
                                        :values="booleanTypes"
                                        :disabled="!editable"
                                    ></base-dropdown>
                                </div>
                                <div v-else-if="columnTypes[colIdx] === 'Value'">
                                    <base-dropdown
                                        :current="inspection[column]"
                                        :values="valueTypes"
                                        :disabled="!editable"
                                    ></base-dropdown>
                                </div>
                                <div v-else-if="columnTypes[colIdx] === 'MeasUnit'">
                                    <base-dropdown
                                        :current="inspection[column]"
                                        :values="measUnitTypes"
                                        :disabled="!editable"
                                    ></base-dropdown>
                                </div>
                                <div v-else-if="columnTypes[colIdx] === 'MeasType'">
                                    <base-dropdown
                                        :current="inspection[column]"
                                        :values="measTpTypes"
                                        :disabled="!editable"
                                    ></base-dropdown>
                                </div>
                                <div v-else :contenteditable='editable'>
                                    {{inspection[column]}}
                                </div>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
            <div class="table-actions">
                <div class="table-manipulation">
                    <div class="add-actions">
                        <button class="add-button" @click="addRow" :disabled="!currentConfiguration">
                            <div class="button-container">
                                <div class="button-icon">
                                    <v-icon name="io-add-circle-sharp" scale="1.5"/>
                                </div>
                                <div class="button-text">ADD ROW</div>
                            </div>
                        </button>
                        <button class="add-button" @click="showColumnDialog" :disabled="!currentConfiguration">
                            <div class="button-container">
                                <div class="button-icon">
                                    <v-icon name="io-add-circle-sharp" scale="1.5"/>
                                </div>
                                <div class="button-text">ADD COL.</div>
                            </div>
                        </button>
                    </div>
                    <div class="delete-actions">
                        <button class="delete-button" @click="deleteRow" :disabled="selectedRow === null">
                            <div class="button-container">
                                <div class="button-icon">
                                    <v-icon name="md-delete-round" scale="1.5"/>
                                </div>
                                <div class="button-text">DELETE ROW</div>
                            </div>
                        </button>
                        <button class="delete-button" @click="deleteColumn" :disabled="selectedColumn === null">
                            <div class="button-container">
                                <div class="button-icon">
                                    <v-icon name="md-delete-round" scale="1.5"/>
                                </div>
                                <div class="button-text">DELETE COL.</div>
                            </div>
                        </button>
                    </div>
                </div>
                <div class="edit-save-container">
                    <button class="edit-button" @click="enableEdit" :disabled="!currentConfiguration">
                        <div class="button-container">
                            <div class="button-icon">
                                <v-icon name="md-modeeditoutline-sharp" scale="1.5"/>
                            </div>
                            <div class="button-text">EDIT</div>
                        </div>
                    </button>
                    <button class="save-button" @click="saveInspectionList" :disabled="!currentConfiguration">
                        <div class="button-container">
                            <div class="button-icon">
                                <v-icon name="ri-save-3-fill" scale="1.5"/>
                            </div>
                            <div class="button-text">SAVE</div>
                        </div>
                    </button>
                </div>
            </div>
        </div>
        <base-dialog title="Add a new column:" :show="showAddColumnDialog" @close="closeAddDialog">
            <template #default>
                <div class="form-control">
                    <label for="column-name">Column Name:</label>
                    <input type="text" name="column-name" id="column-name" v-model.trim="columnName">
                </div>
                <transition name="error">
                    <div class="error" v-if="invalidName">
                        <p>Column name is required and cannot be empty.</p>
                    </div>
                </transition>
                <div class="form-control">
                    <label for="column-type">Column Type:</label>
                    <base-dropdown
                        :current="columnType"
                        :values="availableColumnTypes"
                        width="60%"
                        @update-value="updateColumnType"
                    ></base-dropdown>
                </div>
            </template>
            <template #actions>
                <div class="action-control">
                    <base-button width="7vw" @click="closeAddDialog">Cancel</base-button>
                    <base-button width="7vw" mode="flat" @click="addColumn">Ok</base-button>
                </div>
            </template>
        </base-dialog>
        <base-dialog title="Add a new column:" :show="showCreateTableDialog" @close="closeCreateTableDialog">
            <template #default>
                <div class="form-control">
                    <label for="columns-number">Columns Number:</label>
                    <input type="number" name="columns-number" id="columns-number" v-model.trim="columnsNumber">
                </div>
            </template>
            <template #actions>
                <div class="action-control">
                    <base-button width="7vw" @click="closeCreateTableDialog">Cancel</base-button>
                    <base-button width="7vw" mode="flat" @click="createTable">Ok</base-button>
                </div>
            </template>
        </base-dialog>
        <base-notification :show="showNotification" :timeout="5000" height="15vh">
            <div class="message-wrapper">
                <div class="icon-wrapper">
                    <v-icon :name="notificationIcon" scale="2.5" animation="float" />
                </div>
                <div class="text-wrapper">
                    {{ notificationMessage }}
                </div>
            </div>
        </base-notification>
    </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue';
import { useInspectionListStore, useAuthStore, useConfigurationsStore, useLogStore } from '@/composables/useStore';
import { createLogger } from '@/utils/logger';
import { addErrorToStore, handleApiError } from '@/utils/errorHandler';
import { validateRequired } from '@/utils/validation';

import ExcelJS from 'exceljs';

import UploadInspectionList from '../../inspection_list/UploadInspectionList.vue';
import useNotification from '../../../hooks/notifications.ts';

export default{
    components: {
        UploadInspectionList
    },

    setup() {
        const logger = createLogger('InspectionList');
        
        // Use centralized store composables
        const { inspectionList, currentInspection, loadInspectionList, updateInspectionList } = useInspectionListStore();
        const { currentUser } = useAuthStore();
        const { currentConfiguration } = useConfigurationsStore();
        const { addLog } = useLogStore();
        
        // For remaining store access until fully migrated
        const { store } = useInspectionListStore();

        const showUpload = ref(false);

        // Configuration and user are now from centralized composables

        // Inspections data from centralized store
        const inspections = computed(() => store.getters["inspections/getInspections"]);
        const columnNames = computed(() => store.getters["inspections/getColumnNames"]);
        const columnTypes = computed(() => store.getters["inspections/getColumnTypes"]);

        const editable = ref(false);

        const inspectionTable = ref(null);

        const selectedRow = ref(null);
        const selectedColumn = ref(null);

        const columnName = ref('');
        const columnType = ref('');
        const invalidName = ref(false);

        const columnsNumber = ref(1);

        const columnEditMode = ref(false);

        const showAddColumnDialog = ref(false);
        const showCreateTableDialog = ref(false);

        const availableColumnTypes = ref(['String', 'Boolean', 'Value', 'MeasUnit', 'MeasType']);

        const booleanTypes = ref(['True', 'False']);
        const valueTypes = ref(['Float', 'OK/NOK']);
        const measUnitTypes = ref(['mm', 'N/A']);
        const measTpTypes = ref(['B']);

        const {showNotification, notificationMessage, notificationIcon, notificationTimeout, 
            setNotification, clearNotification} = useNotification();

        function toggleUploadVisibility() {
            showUpload.value = !showUpload.value;
        }

        async function onInspectionListUploaded(file) {
            try {
                const workbook = new ExcelJS.Workbook();
                const buffer = await file.arrayBuffer();
                await workbook.xlsx.load(buffer);

                const worksheet = workbook.getWorksheet('Inspections');
                if (worksheet) {
                    const jsonData = [];
                    const headerRow = worksheet.getRow(1);
                    const headers = [];
                    
                    // Get headers
                    headerRow.eachCell((cell, colNumber) => {
                        headers[colNumber] = cell.value;
                    });

                    // Get data rows
                    worksheet.eachRow((row, rowNumber) => {
                        if (rowNumber > 1) { // Skip header row
                            const rowData = {};
                            row.eachCell((cell, colNumber) => {
                                if (headers[colNumber]) {
                                    rowData[headers[colNumber]] = cell.value;
                                }
                            });
                            jsonData.push(rowData);
                        }
                    });
                    
                    store.dispatch("inspections/setInspections", jsonData);

                    if(inspections.value.length !== 0) {
                        store.dispatch("inspections/setColumnNames", Object.keys(inspections.value[0]));
                        store.dispatch("inspections/setColumnTypes", Array(columnNames.value.length).fill('String'));

                        addLog({
                            type: 'INSPECTION LIST',
                            user: currentUser.value ? currentUser.value.username : 'Unknown',
                            title: 'Inspection List Uploaded',
                            description: `Inspection list: ${file.name} was uploaded.`
                        });
                        
                        logger.info('Inspection list uploaded successfully', { fileName: file.name });
                    }
                }
            } catch (error) {
                logger.error('Failed to read Excel file', error);
                handleApiError(null, null, 'Excel file reading');
                setNotification(3000, 'Error reading Excel file: ' + error.message, 'bi-exclamation-circle-fill');
            }

            showUpload.value = false;
        }

        function convertTableToJSON() {
            let data = [];

            for (let i = 1, row; row = inspectionTable.value.rows[i]; i++) 
            {
                let rowData = {};

                for (let j = 0, col; col = row.cells[j]; j++)
                {
                    let cell = col.firstChild;
                    if(cell.firstChild.firstChild)
                    {
                        rowData[columnNames.value[j]] = cell.firstChild.firstChild.parentElement.value;
                    }
                    else
                    {
                        if(!isNaN(cell.innerHTML))
                        {
                            rowData[columnNames.value[j]] = +cell.innerHTML;
                        }
                        else
                        {
                            rowData[columnNames.value[j]] = cell.innerHTML;
                        }
                    }
                }
                
                data.push(rowData);
            }

            return data;
        }

        async function exportInspectionList() {
            try {
                const data = convertTableToJSON();
                const workbook = new ExcelJS.Workbook();
                const worksheet = workbook.addWorksheet('Inspections');

                if (data.length > 0) {
                    // Add headers
                    const headers = Object.keys(data[0]);
                    worksheet.addRow(headers);

                    // Add data rows
                    data.forEach(row => {
                        const values = headers.map(header => row[header]);
                        worksheet.addRow(values);
                    });

                    // Style the header row
                    const headerRow = worksheet.getRow(1);
                    headerRow.font = { bold: true };
                    headerRow.fill = {
                        type: 'pattern',
                        pattern: 'solid',
                        fgColor: { argb: 'FFE0E0E0' }
                    };
                }

                // Generate buffer and download
                const buffer = await workbook.xlsx.writeBuffer();
                const blob = new Blob([buffer], { 
                    type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' 
                });
                
                const url = window.URL.createObjectURL(blob);
                const link = document.createElement('a');
                link.href = url;
                link.download = 'Inspections.xlsx';
                link.click();
                window.URL.revokeObjectURL(url);
            } catch (error) {
                logger.error('Failed to export Excel file', error);
                setNotification(3000, 'Error exporting Excel file: ' + error.message, 'bi-exclamation-circle-fill');
            }
        }

        function showColumnDialog() {
            columnType.value = availableColumnTypes.value[0];
            columnName.value = '';

            showAddColumnDialog.value = true;
        }

        function showColumnDialogForEdit(idx) {
            columnEditMode.value = true;

            columnType.value = columnTypes.value[idx];
            columnName.value = columnNames.value[idx];

            showAddColumnDialog.value = true;

            selectedColumn.value = idx;
        }

        function showTableDialog() {
            showCreateTableDialog.value = true;
        }

        function createTable() {
            store.dispatch("inspections/setColumnNames", Array(columnsNumber.value).fill(''));
            store.dispatch("inspections/setColumnTypes", Array(columnsNumber.value).fill('String'));

            store.dispatch("inspections/setInspections", []);

            columnsNumber.value = 1;

            closeCreateTableDialog()
        }

        function closeAddDialog() {
            showAddColumnDialog.value = false;
        }

        function closeCreateTableDialog() {
            showCreateTableDialog.value = false;
        }

        function updateColumnType(_, value) {
            columnType.value = value;
        }

        function selectRow(idx) {
            if(!editable.value)
            {
                if(selectedRow.value === idx)
                {
                    selectedRow.value = null;
                }
                else
                {
                    selectedRow.value = idx;
                }
            }
        }

        function addRow() {
            let row = {}

            for(const column of columnNames.value)
            {
                row[column] = '';
            }

            inspections.value.push(row);

            addLog({
                type: 'INSPECTION LIST',
                user: currentUser.value ? currentUser.value.username : 'Unknown',
                title: 'New Row Added',
                description: 'A new row was added to the current inspection list.'
            });
            
            logger.debug('New row added to inspection list');
        }

        function deleteRow(){
            if(selectedRow.value !== null)
            {
                inspections.value.splice(selectedRow.value, 1);
                selectedRow.value = null;
            }

            addLog({
                type: 'INSPECTION LIST',
                user: currentUser.value ? currentUser.value.username : 'Unknown',
                title: 'Row Deleted',
                description: `Row with index ${selectedRow.value} was deleted from the current inspection list.`
            });
            
            logger.debug('Row deleted from inspection list', { rowIndex: selectedRow.value });
        }

        function selectColumn(idx) {
            if(selectedColumn.value === idx)
            {
                selectedColumn.value = null;
            }
            else
            {
                selectedColumn.value = idx;
            }
        }

        function addColumn() {
            // Validate column name using centralized validation
            const validation = validateRequired(columnName.value, 'Column name');
            if (!validation.isValid) {
                invalidName.value = true;
                logger.warn('Column validation failed', { errors: validation.errors });
                return;
            }
            
            invalidName.value = false;
            {
                if(columnEditMode.value)
                {
                    let oldName = columnNames.value[selectedColumn.value];
                    let oldType = columnTypes.value[selectedColumn.value];

                    columnNames.value[selectedColumn.value] = columnName.value;
                    columnTypes.value[selectedColumn.value] = columnType.value;

                    for(const inspection of inspections.value)
                    {
                        inspection[columnName.value] = inspection[oldName];
                        delete inspection[oldName];
                    }

                    columnEditMode.value = false;

                    addLog({
                        type: 'INSPECTION LIST',
                        user: currentUser.value ? currentUser.value.username : 'Unknown',
                        title: 'Column Name Modified',
                        description: `Column name was modified from ${oldName}: ${oldType} to ${columnName.value}: ${columnType.value}`
                    });
                    
                    logger.info('Column modified', { from: `${oldName}:${oldType}`, to: `${columnName.value}:${columnType.value}` });
                }
                else
                {
                    columnNames.value.push(columnName.value);
                    columnTypes.value.push(columnType.value);

                    for(const inspection of inspections.value)
                    {
                        inspection[columnName.value] = '';
                    }

                    addLog({
                        type: 'INSPECTION LIST',
                        user: currentUser.value ? currentUser.value.username : 'Unknown',
                        title: 'New Column Added',
                        description: `A new column with name ${columnName.value} and type ${columnType.value} was added.`
                    });
                    
                    logger.info('New column added', { name: columnName.value, type: columnType.value });
                }

                closeAddDialog();
            }
        }

        function deleteColumn() {
            if(selectedColumn.value !== null)
            {
                columnNames.value.splice(selectedColumn.value, 1);

                let columnName = columnNames.value[selectedColumn.value];

                for(const inspection of inspections.value)
                {
                    delete inspection[columnName];
                }

                selectedColumn.value = null;

                addLog({
                    type: 'INSPECTION LIST',
                    user: currentUser.value ? currentUser.value.username : 'Unknown',
                    title: 'Column Deleted',
                    description: `Column ${columnName} was deleted.`
                });
                
                logger.debug('Column deleted', { columnName });
            }
        }

        function enableEdit() {
            editable.value = !editable.value;
            selectedRow.value = null;
        }

        async function saveInspectionList() {
            let data = convertTableToJSON();

            let inspections = {}

            for(const row of data)
            {
                let inspectionAttr = {}
                for(const [key, value] of Object.entries(row))
                {
                    if(key.includes('Name'))
                    {
                        continue;
                    }
                    else
                    {
                        inspectionAttr[key] = value;
                    }
                }

                inspections[row['Name']] = inspectionAttr;
            }

            try {
                logger.debug('Saving inspection list');
                
                await updateInspectionList({
                    columns: columnNames.value,
                    columnTypes: columnTypes.value,
                    inspections: inspections
                });

                addLog({
                    type: 'INSPECTION LIST',
                    user: currentUser.value ? currentUser.value.username : 'Unknown',
                    title: 'Inspection List Saved',
                    description: `Inspection list was saved.`
                });
                
                logger.info('Inspection list saved successfully');
            } catch(err) {
                logger.error('Failed to save inspection list', err);
                setNotification(3000, err.message || err, 'bi-exclamation-circle-fill');
            }
        }

        onMounted(async () => {
            logger.lifecycle('mounted', 'InspectionList component mounted');
            
            if(currentConfiguration.value) {
                try {
                    logger.debug('Loading inspection list');
                    await loadInspectionList();
                    logger.info('Inspection list loaded successfully');
                } catch(error) {
                    logger.error('Failed to load inspection list', error);
                }
            }
        });

        return {
            showUpload,
            inspections,
            columnNames,
            columnTypes,
            columnsNumber,
            inspectionTable,
            editable,
            selectedRow,
            selectedColumn,
            showAddColumnDialog,
            showCreateTableDialog,
            columnName,
            columnType,
            invalidName,
            availableColumnTypes,
            booleanTypes,
            valueTypes,
            measUnitTypes,
            measTpTypes,
            currentConfiguration,
            showNotification,
            notificationIcon,
            notificationMessage,
            notificationTimeout,
            exportInspectionList,
            toggleUploadVisibility,
            onInspectionListUploaded,
            selectRow,
            addRow,
            deleteRow,
            selectColumn,
            addColumn,
            deleteColumn,
            enableEdit,
            showColumnDialog,
            showColumnDialogForEdit,
            showTableDialog,
            createTable,
            closeAddDialog,
            closeCreateTableDialog,
            updateColumnType,
            saveInspectionList,
            clearNotification
        }
    }
}
</script>

<style scoped>
.flex-container {
    display: flex;
    flex-direction: column;
    justify-content: flex-start;
    align-items: center;
    width: 95%;
    height: 100%;
    color: white;
    margin: auto;
}

.content-wrapper {
    display: flex;
    flex-direction: column;
    margin-top: 1vh;
    width: 100%;
    height: 100%;
}

button {
    padding: 0;
}

.button-container {
    display: flex;
    width: 100%;
    height: 4vh;
    padding: 4px;
    justify-content: center;
    align-items: center;
}

.button-icon {
    height: 100%;
    display: flex;
    align-items: center;
}

.button-text {
    height: 100%;
    display: flex;
    align-items: center;
    font-size: medium;
}

.upload {
    display: flex;
    justify-content: center;
    margin-top: 1vh;
}

.table-wrapper {
    margin-top: 3vh;
    height: 100%;
    overflow-y: auto;
}

/* table {
    border-collapse: collapse;
    border-radius: 1em;
}

.inspections-table {
    width: 100%;
    height: 100%;
}

table thead {
    background-color: rgba(204, 161, 82);
}

th {
    padding: 1vh 1vw;
}

.inspections-table td {
    height: 2vh;
    margin: 10px;
    padding: 10px;
    border: 1px solid rgb(147, 144, 144);
} */
table {
    border-collapse: collapse;
    border-radius: 1em;
}

.inspections-table {
    background-color: rgb(0, 0, 0);
    color: rgb(255, 255, 255);
    width: 100%;
    border-radius: 1em;
    border-collapse: collapse;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.26);
}

th {
    background-color: rgba(204, 161, 82);
    border-radius: 1%;
    color: white;
}

.inspections-table th{
    color: white;
    height: 5vh;
    position: sticky;
    user-select: none;
}

.inspections-table td {
    height: 5.5vh;
}

.selected-row {
    background-color: gray;
}

.selected-column {
    background-color: rgb(126, 99, 50);
}

.table-wrapper::-webkit-scrollbar {
    display: none;
}

.table-actions {
    margin-top: 1vh;
    height: 15vh;
    display: flex;
    justify-content: space-between;
}

.add-actions {
    display: flex;
    margin-bottom: 1.5vh;
}

.delete-actions {
    display: flex;
}

.add-button {
    background-color: green;
    color: white;
    width: 10vw;
    margin-right: 1vw;
}

.add-button:hover {
    border: 1px solid rgb(0, 86, 0);
}

.delete-button {
    background-color: crimson;
    color: white;
    width: 10vw;
    margin-right: 1vw;
}

.delete-button:hover {
    border: 1px solid rgb(120, 11, 33);
}

.edit-save-container {
    display: flex;
    flex-direction: column;
}

.edit-button {
    background-color: gray;
    color: white;
    width: 10vw;
    margin-bottom: 1vh;
}

.edit-button:hover {
    border: 1px solid rgb(77, 77, 77);
}

.save-button {
    background-color: rgb(96, 96, 214);
    color: white;
    width: 10vw;
    margin-right: 1vw;
}

.save-button:hover {
    border: 1px solid rgb(54, 54, 122);
}

button:disabled,
button[disabled]{
  border: 1px solid #999999;
  background-color: #cccccc;
  color: #666666;
  cursor: not-allowed;
}

.form-control {
    background-color: inherit;
    border: none;
    color: white;
    display: flex;
    justify-content: space-between;
}

.error {
    color: red;
}

input {
    width: 60%;
    background-color: rgb(56, 54, 54);
    border: none;
    color: white;
}

.message-wrapper {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
}

.icon-wrapper {
    display: flex;
    justify-content: center;
    align-items: center;
    margin-bottom: 3%;
}

.text-wrapper {
    font-size: 100%;
    width: 95%;
    text-align: center;
}

.error-enter-from,
.error-leave-to {
    opacity: 0;
    transform: scale(0.8);
}

.error-enter-to,
.error-leave-from {
    opacity: 1;
    transform: scale(1);
}

.error-enter-active {
    transition: all 0.3s ease-out;
}

.error-leave-active {
    transition: all 0.3s ease-in;
}
</style>