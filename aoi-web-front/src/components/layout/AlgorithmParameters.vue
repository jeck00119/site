<template>
    <div class="parameters-wrapper" :style="{height: height}">
        <h3>Parameters:</h3>
        <div class="form-control" v-for="attribute in algorithmAttributes" :key="generateID">
            <div class="parameter-wrapper" v-if="attribute.type === 'integer' || attribute.type === 'float'">
                <div class="label-wrapper">
                    <label :for="attribute.name">{{ getParameterDisplayName(attribute.name) }}:</label>
                </div>
                <div class="value-wrapper">
                    <base-integer-input
                        width="90%"
                        :current="parameters[attribute.name] ?? attribute.default"
                        :name="attribute.name"
                        @update-value="updateValue"
                    ></base-integer-input>
                </div>
            </div>
            <div class="parameter-wrapper" v-else-if="attribute.type === 'bool'">
                <div class="label-wrapper">
                    <label :for="attribute.name">{{ getParameterDisplayName(attribute.name) }}:</label>
                </div>
                <div class="value-wrapper">
                    <base-checkbox
                        :current="parameters[attribute.name] ?? attribute.default"
                        :name="attribute.name"
                        @update-value="updateValue"
                    ></base-checkbox>
                </div>
            </div>
            <div class="parameter-wrapper" v-else-if="attribute.type === 'dropdown'">
                <div class="label-wrapper">
                    <label :for="attribute.name">{{ getParameterDisplayName(attribute.name) }}:</label>
                </div>
                <div class="value-wrapper">
                    <base-dropdown
                        width="90%"
                        :current="parameters[attribute.name] ?? attribute.default"
                        :values="attribute.values"
                        :name="attribute.name"
                        @update-value="updateValue"
                    ></base-dropdown>
                </div>
            </div>
            <div class="parameter-wrapper" v-else-if="attribute.type === 'string'">
                <div class="label-wrapper">
                    <label :for="attribute.name">{{ getParameterDisplayName(attribute.name) }}:</label>
                </div>
                <div class="value-wrapper">
                    <base-text-input 
                        width="90%"
                        :current="parameters[attribute.name] ?? attribute.default"
                        :name="attribute.name"
                        @update-value="updateValue"
                    ></base-text-input>
                </div>
            </div>
            <div class="parameter-wrapper" v-else-if="attribute.type === 'color'">
                <div class="label-wrapper">
                    <label :for="attribute.name">{{ getParameterDisplayName(attribute.name) }}:</label>
                </div>
                <div class="value-wrapper">
                    <base-color-picker
                        width="10vw"
                        :current="parameters[attribute.name] ?? attribute.default"
                        :name="attribute.name"
                        @update-value="updateValue"
                    ></base-color-picker>
                </div>
            </div>
            <div class="parameter-wrapper" v-else-if="attribute.type === 'fileloader'">
                <!-- <div class="label-wrapper">
                    <label :for="attribute.name">{{ getParameterDisplayName(attribute.name) }}:</label>
                </div> -->
                <div class="value-wrapper load">
                    <base-file-loader 
                        width="100%"
                        :path="attribute.path"
                        :update="attribute.update"
                        @files-dropped="filesDropped"
                    >
                        <div class="load-info">
                            {{ fileLoadMessage }}
                        </div>
                    </base-file-loader>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import { ref, computed } from 'vue';
import { useStore } from 'vuex';

import { uuid } from "vue3-uuid";

export default {
    props: ['type', 'algorithmIdx' ,'algorithmAttributes', 'parameters', 'height'],

    setup(props) {
        const fileLoadMessage = ref('Drop File Here');

        const store = useStore();

        function getParameterDisplayName(parameter) {
            return parameter.split('_').map((value) => value[0].toUpperCase() + value.slice(1)).join(' ');
        }

        const values = computed(function() {
            const res = {}

            for(const key in props.algorithmAttributes)
            {
                if(props.parameters.length > 0)
                {
                    res[props.algorithmAttributes[key].name] = props.parameters[key];
                }
                else
                {
                    res[props.algorithmAttributes[key].name] = props.algorithmAttributes[key].default;
                }
            }

            return res;
        });

        function updateValue(name, value)
        {
            if(props.type === 'custom_component')
            {
                let idx = parseInt(props.algorithmIdx, 10);
                store.dispatch("algorithms/updateCurrentBasicAlgorithmProperty", {
                    idx: idx,
                    name: name,
                    value: value
                });
            }
            else if(props.type === 'reference')
            {
                store.dispatch("algorithms/updateCurrentReferenceAlgorithmProperty", {
                    name: name,
                    value: value
                });
            }
            else
            {
                store.dispatch("algorithms/updateCurrentAlgorithmProperty", {
                    name: name,
                    value: value
                });
            }
        }

        async function filesDropped(path, update, value)
        {
            fileLoadMessage.value = 'Please Wait...';

            const file = value[0];

            const formData = new FormData();
            formData.append('file', file);
            formData.append('path', path);

            try {
                await store.dispatch("algorithms/uploadResource", formData);

                if(update)
                {
                    if(props.type === 'custom_component')
                    {
                        let idx = parseInt(props.algorithmIdx, 10);
                        store.dispatch("algorithms/updateCurrentBasicAlgorithmAttributes", {
                            idx: idx,
                            name: update,
                            value: file.name
                        });
                    }
                    else if(props.type === 'reference')
                    {
                        store.dispatch("algorithms/updateCurrentReferenceAlgorithmAttributes", {
                            name: update,
                            value: file.name
                        });
                    }
                    else
                    {
                        store.dispatch("algorithms/updateCurrentAlgorithmAttributes", {
                            name: update,
                            value: file.name
                        });
                    }
                }

                fileLoadMessage.value = 'File Loaded';
            }
            catch(error) {
                fileLoadMessage.value = 'An error occured. Try again.';
            }
            
            setTimeout(() => {
                fileLoadMessage.value = 'Drop File Here';
            }, 3000);
        }

        return {
            values,
            fileLoadMessage,
            getParameterDisplayName,
            updateValue,
            filesDropped,
            generateID: uuid.v4()
        }
    }
}
</script>

<style scoped>
.parameters-wrapper {
    overflow-y: auto;
}

.form-control {
    background-color: inherit;
    border: none;
    color: inherit;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    height: 5vh;
}

.parameter-wrapper {
    display: flex;
    flex-direction: row;
    width: 100%;
    height: 100%;
    /* background-color: rgb(0, 47, 255); */
    /* margin-bottom: 2px; */
}

.label-wrapper {
    width: 60%;
    max-width: 100%;
    font-size: 80%;
    display: flex;
    justify-content: flex-start;
    align-items: center;
}

.value-wrapper {
    width: 40%;
    display: flex;
    justify-content: flex-end;
}

.load {
    width: 100%;
    height: 10vh;
}

.load-info {
    width: 100%;
    height: 100%;
    display: flex;
    justify-content: center;
    align-items: center;
}
</style>