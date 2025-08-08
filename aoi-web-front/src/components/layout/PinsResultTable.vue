<template>
    <div class="table-wrapper">
        <table class="result-table">
            <thead>
                <tr>
                    <th></th>
                    <th v-for="i in pinsNumber">P{{i}}</th>
                    <!-- <th>Value</th> -->
                </tr>
            </thead>
            <tr v-for="i in 2" :key="i" v-memo="[xValues.length, i]">
                <td style="background-color: black;">{{ i % 2 === 0 ? 'Y': 'X'}}</td>
                <td v-for="p in xValues.length" :key="p" class="table-data-pass" :class='{"failed-inspection": failed(i, p)}'>{{ outputValue(i, p) }}</td>
                <!-- <td>{{ value.value }}</td> -->
            </tr>
        </table>
    </div>
</template>

<script>
import { ref, watch } from 'vue';
export default {
    props: ['dimensions', 'data'],
    setup(props){
        const [x, y] = getXValuesSorted();

        const xValues = ref(x);
        const yValues = ref(y);
        const zValues = ref([]);

        function failed(rowIdx, pinIdx) {
            if(xValues.value.length === 0 || yValues.value.length === 0)
            {
                return false;
            }
            return rowIdx % 2 === 1 ? xValues.value[pinIdx-1].pass === false : yValues.value[pinIdx-1].pass === false;
        }

        function outputValue(rowIdx, pinIdx) {
            if(xValues.value.length === 0 || yValues.value.length === 0)
            {
                return "";
            }
            return rowIdx % 2 === 1 ? xValues.value[pinIdx-1].value : yValues.value[pinIdx-1].value;
        }

        function getPinsNumber() {
            return Object.keys(props.data).length / props.dimensions;
        }

        const pinsNumber = ref(getPinsNumber());

        watch(props, () => {
            [xValues.value, yValues.value] = getXValuesSorted();
            pinsNumber.value = getPinsNumber();
        });

        function compareByPinNumber(a, b) {
            const pin1 = Object.keys(a)[0];
            const pin2 = Object.keys(b)[0];

            const numbers1 = pin1.match(/\d+/g);
            const numbers2 = pin2.match(/\d+/g);

            const pin_number1 = parseInt(numbers1[0]);
            const pin_number2 = parseInt(numbers2[0]);

            if(pin_number1 < pin_number2)
            {
                return -1;
            }

            if(pin_number1 > pin_number2)
            {
                return 1;
            }

            return 0;
        }

        function compareByDimension(a, b){
            const pin1 = Object.keys(a)[0];
            const pin2 = Object.keys(b)[0];

            if(pin1.slice(-1) < pin2.slice(-1))
            {
                return -1;
            }

            if(pin1.slice(-1) > pin2.slice(-1))
            {
                return 1;
            }

            return 0;
        }

        function getXValuesSorted() {
            const pinsData = [props.data].flat();

            pinsData.sort(compareByPinNumber);
            pinsData.sort(compareByDimension);

            const x = [];
            const y = [];

            let idx = 0;

            for(const key in pinsData[0])
            {
                if(idx % 2 === 0)
                {
                    x.push(pinsData[0][key]);
                }
                else
                {
                    y.push(pinsData[0][key]);
                }
                idx += 1;
            }

            return [x, y];
        }

        return {
            xValues,
            yValues,
            pinsNumber,
            failed,
            outputValue
        }
    }
}
</script>

<style scoped>
table {
    border-collapse: collapse;
    width: 100%;
    background-color: antiquewhite;
}

.table-wrapper {
    height: 10vh;
    background-color: red;
    overflow-y: auto;
    width: 100%;
    margin-top: 1vh;
}

.table-wrapper::-webkit-scrollbar {
    display: none;
}

.table-wrapper thead th {
    background-color: black;
    position: sticky;
    top: 0;
    z-index: 1;
}

.result-table {
    background-color: rgb(0, 0, 0);
    color: rgb(255, 255, 255);
    width: 100%;
    border-collapse: collapse;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.26);
    margin: 0;
}

.result-table tr{
    border-bottom: 1px solid #696464;
}

.result-table td {
    padding: 5px;
}

.table-data-pass{
    background-color: #524d4d;
}

.failed-inspection {
    background-color: rgba(255, 0, 0, 0.658);
    animation-name: failed-inspection-anim;
    animation-duration: 1s;
    animation-iteration-count: infinite;
    animation-direction: alternate;
}

@keyframes failed-inspection-anim {
    from {background-color: #524d4d;}
    to {background-color: rgba(255, 0, 0, 0.658);}
}
</style>