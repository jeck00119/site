<!-- <template>
    <div class="camera-view">
        <p>Camera View</p>
        <camera-scene
            width="31vw"
            height="60vh"
            :show="true"
            :camera-feed="true"
            :feed-location="feedLocation"
            :static-images="[]"
            :id="1"
            canvas-id="camera-scene-canvas"
            :graphics="currentGraphics"
            @graphics-changed="updateGraphics"
        ></camera-scene>
    </div>
</template>

<script>
import CameraSceneVue from '../camera/CameraScene.vue';
import { ref, computed, onMounted, onBeforeUnmount } from 'vue';
import { useStore } from 'vuex';
import graphic from '../../utils/graphics';


export default{
    components:{
        CameraSceneVue
    },

    setup(){
        const store = useStore();

        const feedLocation = ref('');

        const showCamera = ref(false);


        const currentGraphics = computed(function() {
            return store.getters["graphics/getCurrentGraphics"];
        });

        function updateGraphics() {
            const graphicItems = store.getters["graphics/getCurrentGraphics"];
            const canvas = store.getters["graphics/getCanvas"];

            graphicsObject = graphic.getGraphicsProps(graphicItems, canvas);
        }
        
        function changeCameraStatus(value) {
            showCamera.value = value;
        }

        return{
            feedLocation,
            showCamera,
            currentGraphics,
            updateGraphics,
            changeCameraStatus
        }
    }
}

</script>

<style scoped>
.camera-view{
    background-color: rgb(0, 0, 0);
    width:100%;
    height:84.3%;
    margin-left:1%;
    margin-right:1%;
    border-radius:20px;

}

p{
    background-color: rgb(37, 36, 36);
    color:rgba(204, 161, 82);
    border-top-right-radius:20px;
    border-top-left-radius:20px;
}
</style> -->