<template>
    <div class="flex-container">
        <div class="aoi-logo-container">
            <img class="aoi-logo" src="../../../assets/icons/aoi-logo.png" alt="AOI Logo">
        </div>
        <div class="home-header">
            <div class="hella-logo-container">
                <img class="hella-logo" src="../../../assets/icons/hella-logo-white.png" alt="Hella Logo">
            </div>
        </div>
        <div class="content-container">
            <div class="inspection-container">
                <div class="inspection-img-container">
                    <img class="inpection-cover" src="../../../assets/icons/pcb-inspection-removebg.png" alt="Inspection Showcase">
                </div>
                <div class="inspection-content">
                    <h1 style="text-align: left">System Control and Feedback</h1>
                    <p class="card-information">System controls and results visualization are available on the Inspection Results page.</p>
                    
                    <base-button-rectangle
                        width="12vw"
                    >
                        <router-link :to="'/inspections-and-results'" style="width: 100%; padding: 0; margin: 0; display: block;">
                            <div class="button-container-router">
                                <div class="button-icon">
                                    <v-icon name="la-clipboard-list-solid" scale="1.5"/>
                                </div>
                                <div class="button-text">Go To Inspection Results</div>
                            </div>
                        </router-link>
                    </base-button-rectangle>
                </div>
            </div>
            <div class="algorithms-configuration-container">
                <div class="component-config-container">
                    <div class="cover-container">
                        <img src="../../../assets/icons/component_config_cover.png" alt="">
                    </div>
                    <div class="information-container">
                        <h2 style="height: 30%; width:100%; font-size:2vmax;">Component Configuration</h2>
                        <p style="height: 25%; margin-top: 5%; font-size: 90%;">Configure the components that are used in the inspection process.</p>
                        <base-button-rectangle
                            width="80%"
                        >
                            <router-link :to="'/inspections-and-results'" style="width: 100%; padding: 0; margin: 0; display: block;">
                                <div class="button-container-router">
                                    <div class="button-icon">
                                        <v-icon name="md-settingsinputcomponent" scale="1.5"/>
                                    </div>
                                    <div class="button-text">Go To Component Configuration</div>
                                </div>
                            </router-link>
                        </base-button-rectangle>
                    </div>
                </div>
                <div class="reference-config-container">
                    <div class="cover-container reference-cover">
                        <img src="../../../assets/icons/reference_cover.jpg" alt="">
                    </div>
                    <div class="information-container">
                        <h2 style="height: 30%; width:100%; font-size:2vmax;">Reference Configuration</h2>
                        <p style="height: 25%; margin-top: 5%; font-size: 90%;">Configure the references that are used in the inspection process.</p>
                        <base-button-rectangle
                            width="80%"
                        >
                            <router-link :to="'/inspections-and-results'" style="width: 100%; padding: 0; margin: 0; display: block;">
                                <div class="button-container-router">
                                    <div class="button-icon">
                                        <v-icon name="si-target" scale="1.5"/>
                                    </div>
                                    <div class="button-text">Go To Reference Configuration</div>
                                </div>
                            </router-link>
                        </base-button-rectangle>
                    </div>
                </div>
                <div class="custom-component-config-container">
                    <div class="cover-container custom-component-cover">
                        <img src="../../../assets/icons/custom_component_cover.jpg" alt="">
                    </div>
                    <div class="information-container">
                        <h2 style="height: 30%; width:100%; font-size:2vmax;">Custom Component Configuration</h2>
                        <p style="height: 25%; margin-top: 5%; font-size: 90%;">Configure the custom components that are used in the inspection process.</p>
                        <base-button-rectangle
                            width="80%"
                        >
                            <router-link :to="'/inspections-and-results'" style="width: 100%; padding: 0; margin: 0; display: block;">
                                <div class="button-container-router">
                                    <div class="button-icon">
                                        <v-icon name="md-dashboardcustomize" scale="1.5"/>
                                    </div>
                                    <div class="button-text">Go To Custom Component Configuration</div>
                                </div>
                            </router-link>
                        </base-button-rectangle>
                    </div>
                </div>
                <div class="inspection-list-container">
                    <div class="cover-container">
                        <img src="../../../assets/icons/inspection_list_cover.jpg" alt="">
                    </div>
                    <div class="information-container">
                        <h2 style="height: 30%; width:100%; font-size:2vmax;">Inspection List</h2>
                        <p style="height: 25%; margin-top: 5%; font-size: 90%;">View the list of inspections that have been performed.</p>
                        <base-button-rectangle
                            width="80%"
                        >
                            <router-link :to="'/inspections-and-results'" style="width: 100%; padding: 0; margin: 0; display: block;">
                                <div class="button-container-router">
                                    <div class="button-icon">
                                        <v-icon name="fa-list-ul" scale="1.5"/>
                                    </div>
                                    <div class="button-text">Go To Inspection List</div>
                                </div>
                            </router-link>
                        </base-button-rectangle>
                    </div>
                </div>
            </div>
            <div class="cnc-container">
                <div class="cnc-content">
                    <h1 style="text-align: left">CNC Control</h1>
                    <p class="card-information">Navigate the world of CNC with ease on our control page. Adjust settings, save and load locations, and fine-tune feed rates effortlessly. With intuitive move controls and precise feedback, mastering your machine is just a click away. Explore the simplicity of configuration options and streamline your workflow for optimal results.</p>
                    
                    <base-button-rectangle
                        width="12vw"
                    >
                        <router-link :to="'/inspections-and-results'" style="width: 100%; padding: 0; margin: 0; display: block;">
                            <div class="button-container-router">
                                <div class="button-icon">
                                    <v-icon name="co-camera-control" scale="1.5"/>
                                </div>
                                <div class="button-text">Go To CNC Machine Control Panel</div>
                            </div>
                        </router-link>
                    </base-button-rectangle>
                </div>
                <div class="cnc-img-container">
                    <img class="cnc-cover" src="../../../assets/icons/cnc_machine_cover.jpg" alt="Inspection Showcase">
                </div>
            </div>
            <div class="algorithm-debug-container">
                <div class="algorithm-img-container">
                    <img class="algorithm-cover" src="../../../assets/icons/algorithm_debug_cover.png" alt="Inspection Showcase">
                </div>
                <div class="algorithm-debug-content">
                    <h1 style="text-align: left">Algorithm Debug</h1>
                    <p class="card-information">Welcome to our Algorithm Playground! Explore the fascinating world of algorithms and tweak their parameters to see how they behave. Dive into this interactive space where you can experiment, learn, and fine-tune algorithms to suit your needs. Whether you're a seasoned developer or just curious about the inner workings of algorithms, this is the perfect place to test and play with different configurations. Get ready to unleash your creativity and discover the power of algorithms firsthand!</p>
                    
                    <base-button-rectangle
                        width="12vw"
                    >
                        <router-link :to="'/inspections-and-results'" style="width: 100%; padding: 0; margin: 0; display: block;">
                            <div class="button-container-router">
                                <div class="button-icon">
                                    <v-icon name="bi-bug-fill" scale="1.5"/>
                                </div>
                                <div class="button-text">Go To Algorithm Debug</div>
                            </div>
                        </router-link>
                    </base-button-rectangle>
                </div>
            </div>
        </div>
        <div class="primary-buttons-container">
            <div class="button-container" v-for="button in buttons" :key="button.name"> 
                <base-button class="primary-button" :class="{primaryclicked:button.clicked}" @click="buttonClicked(button)"> 
                    <div class="inner-button">
                        <div class="icon-wrapper" :class="button.clicked ? 'wrapleft' : 'wrapright'" >
                            <div class="icon-div" :class="button.clicked ? 'iconleft' : 'iconright'">
                                <font-awesome-icon :icon="button.icon"/>
                            </div>
                            <div class="name-wrapper" :class="button.clicked ? 'nameleft' : 'nameright'">
                                {{ button.name }}
                            </div>
                        </div>
                        <transition name="clicked-anim">
                            <div v-if="button.clicked" class="submenu">
                                <div class="subpage">
                                    <div class="first-column">
                                        <div class="submenu-button" v-for="subpage in button.subpages.slice(0,3)">
                                            <router-link class="router-link" :to="'/' + subpage.split(' ').join('-').toLowerCase()">
                                                <button  class="sub-button" v-if="subpage != null">{{subpage}}</button>  
                                            </router-link>
                                        </div>
                                    </div> 
                                    <div class="second-column">     
                                        <div class="submenu-button" v-for="subpage in button.subpages.slice(3)">
                                            <router-link class="router-link" :to="'/' + subpage.split(' ').join('-').toLowerCase()">
                                                <button class="sub-button" v-if="subpage != null">{{subpage}}</button>  
                                            </router-link>
                                        </div>                   
                                    </div>  
                                </div>                               
                            </div>
                        </transition>
                    </div>
                </base-button>
            </div>
            <div class="button-container" v-for="button in configuration">
                <router-link style="width: 100%; height: 100%" :to="'/configurations'">              
                    <base-button class="config-button" @click="buttonClicked(button)">
                        <div class="inner-button">
                            <div class="icon-wrapper"  >
                                <div class="icon-div" >
                                    <font-awesome-icon :icon="button.icon"/>
                                </div>
                                <div class="name-wrapper" > 
                                    {{ button.name }}
                                </div>
                            </div>    
                        </div>
                    </base-button>
                </router-link>

            </div>
        </div>
    </div>
</template>

<script>

import { useStore } from 'vuex';
import NavPrimaryButton from '../../layout/NavPrimaryButton.vue';
import { ref, computed, onMounted, onUpdated, onBeforeUpdate } from 'vue';


export default{
    components:{
        NavPrimaryButton
    },
 
    setup(_, context) {
        const buttons = ref([
            {
                name: "HOME",
                icon: 'house',
                subpages: ["AOI", "Inspections and Results"],
                clicked: false
            },
            {
                name: "INSPECTIONS",
                icon: 'magnifying-glass-chart',
                subpages: ["Components", "Identification", "References", "Custom Components", "Inspection List"],
                clicked: false
            },
            {
                name: "TOOLS",
                icon: 'screwdriver-wrench',
                subpages: ["CNC Machine", "Algorithm Debug", "Log"],
                clicked: false
            },
            {
                name: "SETTINGS",
                icon: 'gear',
                subpages: ["Itac Settings", "System Settings", "Image Sources"],
                clicked: false
            },
            {
                name: "AUTHENTICATION",
                icon: 'user',
                subpages: ["Signup", "Login"],
                clicked: false
            },
            {
                name: "ABOUT",
                icon: 'circle-info',
                subpages: ["Help"],
                clicked: false
            }
        ]);
        const configuration = ref([
            {
                name: "CONFIGURATIONS",
                icon: 'clipboard-check',
                subpages: ["Configurations"],
                clicked: false
            }])

        function buttonClicked(button) {
            button.clicked = !button.clicked;
        }

        return {
            buttons,
            configuration,
            buttonClicked
        }
        
    }
    
}
</script>

<style scoped>
.flex-container {
    display: block;
    width: 100%;
    height: 90vh;
    color: white;
    position: relative;
    overflow-y: auto;
}

.flex-container::-webkit-scrollbar { 
    display: none;  /* Safari and Chrome */
}

.home-header {
    width: 100%;
    height: 7%;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.content-container {
    display: flex;
    flex-direction: column;
    margin-top: 8vh;
}

.inspection-container {
    display: flex;
    justify-content: space-around;
    width: 100%;
    position: relative;
    background-color: rgb(204, 161, 82);
    background: radial-gradient(#fa709a, #fee140);
    border-radius: 20px;
}

.inspection-img-container {
    width: 50%;
    height: 100%;
}

.inspection-cover {
    max-width: 50%;
    height: auto;
    object-fit: cover;
    margin: 0;
}

.inspection-content {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: flex-start;
}

.cnc-container {
    display: flex;
    justify-content: space-around;
    width: 100%;
    position: relative;
    background: linear-gradient(109.6deg, rgba(0, 0, 0, 0.93) 11.2%, rgb(63, 61, 61) 78.9%);
    border-radius: 20px;
    margin-top: 3%;
    padding: 3%;
}

.cnc-img-container {
    width: 50%;
    height: 100%;
}

.cnc-cover {
    max-width: 50%;
    height: auto;
    object-fit: cover;
    margin: 0;
}

.cnc-content {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: flex-start;
    width: 50%;
}

.algorithm-debug-container {
    display: flex;
    justify-content: space-around;
    width: 100%;
    position: relative;
    background: linear-gradient(120deg, #f6d365 0%, #fda085 100%);
    border-radius: 20px;
    margin-top: 3%;
    padding: 3%;
    color: black;
}

.algorithm-img-container {
    width: 50%;
    height: 100%;
}

.algorithm-cover {
    max-width: 50%;
    height: auto;
    object-fit: cover;
    margin: 0;
}

.algorithm-debug-content {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: flex-start;
    width: 50%;
}

.card-information {
    margin-top: 2%;
    text-align: left;
}

.button-container-router {
    display: flex;
    width: 100%;
    height: 6vh;
    padding: 4px;
    justify-content: center;
    align-items: center;
    color: rgba(204, 161, 82);
}

.button-icon {
    height: 100%;
    display: flex;
    justify-content: center;
    align-items: center;
}

.button-text {
    height: 100%;
    display: flex;
    justify-content: center;
    align-items: center;
    font-size: 80%;
}

.algorithms-configuration-container {
    display: flex;
    justify-content: space-around;
    margin-top: 2%;
    height: 50vh;
}

.component-config-container {
    width: 20%;
    height: 100%;
    background: linear-gradient(109.6deg, #D4145A 11.2%, #FBB03B 78.9%);
    border-radius: 10px;
}

.cover-container {
    height: 42.5%;
    width: auto;
    background-color: white;
}

.cover-container img {
    max-width: 100%;
    height: auto;
    object-fit: cover;
    margin: 0;
}

.reference-cover {
    background-color: rgb(44, 2, 66);
}

.custom-component-cover {
    background-color: rgb(248, 242, 216);
}

.reference-config-container {
    width: 20%;
    height: 100%;
    background: radial-gradient(#FF512F, #DD2476);
    color: white;
    border-radius: 20px;
}

.custom-component-config-container {
    width: 20%;
    height: 100%;
    background: radial-gradient(#D4145A, #FBB03B);
    border-radius: 20px;
}

.inspection-list-container {
    width: 20%;
    height: 100%;
    background-color: rgba(204, 161, 82);
    background: linear-gradient(109.6deg, #FF512F 11.2%, #DD2476 78.9%);
    border-radius: 20px;
}

.information-container {
    display: flex;
    flex-direction: column;
    justify-content: space-around;
    align-items: center;
    /* padding: 1%; */
    height: 56.5%;
}

.hella-logo-container {
    display: flex;
    justify-content: flex-end;
    align-items: center;
    height: 100%;
    width: 100%;
    margin-top: 2%;
}

.hella-logo {
    max-width: 100%;
    height: auto;
    object-fit: cover;
    margin: 0;
}

.aoi-logo-container {
    /* display: flex;
    justify-content: flex-end;
    align-items: center; */
    width: 100%;
    height: 15%;
    position: absolute;
    top: 0%;
    left: 0%;
}

.aoi-logo {
    max-width: 100%;
    height: auto;
    object-fit: cover;
    width: 13%;
}


img {
    max-width: 100%;
    max-height: 100%;
}

.primary-buttons-container{
    display: flex; 
    flex-wrap: wrap;
    justify-content: center;
    margin: 1%;
    height: 95%;
    background-color: black;
}

.button-container {
    height: 22%;
    width: 50%;
    display: flex;
    flex-wrap: wrap;
    flex-direction: row;
    margin-bottom: 1%;
    justify-content: center;
}

.primary-button {
    font-size: 2vw;
    font-weight: bold;
    width: 80%;
    position: relative;
    z-index: 1;
    border: none;
}

.primaryclicked{
    background-image: linear-gradient(to right, black , rgb(55, 54, 54));
}

.config-button{
    font-size: 2vw;
    font-weight: bold;
    width:100%;
    height: 100%;
    border:none;
}

.icon-wrapper {
    display:block;
    align-items: center;
    justify-content: center;
}

.icon-div{
    display: flex;
    justify-content: center;
}

.router-link{
    height:100%;
    width:80%;
    display:flex;
    align-items: center;
}

.submenu {
    position:absolute;
    display: flex;
    justify-content: flex-start;
    align-items: center;
    left:50%;
    width: 50%;
    height: 100%;
}

.subpage{
    font-size: 90%;
    display: flex;
    width: 100%;
    position:relative;
    height: 100%;
    align-items: center;
}

.first-column {
    position:relative;
    height: 100%;
    width: 100%;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-content: center;
}

.second-column{
    position:relative;
    height: 100%;
    width: 100%;
    display: flex;
    flex-direction: column;
    justify-content: center;
}

.submenu-button{
    height:70%;
    display:flex;
    align-self: center;
}

.sub-button{
    width:10vw;
    height:5vh;
    background-color:transparent;
    border:none;
    color:rgba(204, 161, 82);
    border-radius: 20px;
    font-size: 50%;
    font-weight: bold;
    display:flex;
    justify-content: center;
    align-items: center;
}

.sub-button:hover{
    color:white;
    /* background : rgba(204, 161, 82);     */
    /* background-image: radial-gradient( rgba(204, 161, 82) 60%, transparent ); */
    background-image: linear-gradient(to right, rgba(204, 161, 82), transparent );
    /* -moz-box-shadow: 0 0 50px 20px rgba(204, 161, 82);
    box-shadow: 0 0 50px 20px rgba(204, 161, 82); */


}

.name-wrapper{
    display:block;
    
}

.inner-button {
    display:inline-flex;
    align-items: center;
    justify-content: center;
    height: 100%;
    width: 100%;
}

.clicked-anim-enter-from,
.clicked-anim-leave-to{
    opacity: 0;
    transform: translateX(5vw);
}

.clicked-anim-enter-to,
.clicked-anim-leave-from{
    opacity: 1;
    transform: translateX(0);
}

.clicked-anim-enter-active{
    transition: all 0.5s ease-in;

}

.clicked-anim-leave-active{
    transition: all 0.3s ease-in;
}
 
.iconleft{
    animation: slide-left 0.5s ease-in forwards;
    position:relative;
}

.iconright{
    animation: slide-right 0.5s forwards;
    position:relative;
}

.wrapleft{
    animation: zoom-out 0.5s ease-in forwards;
    /* visibility:hidden; */
}

.wrapright{
    animation: zoom-in 0.5s ease-out forwards;
    /* visibility:visible; */

} 

.nameleft{
    animation: name-dissappear 0.5s ease-in forwards;
}

.nameright{
    animation: name-appear 0.5s ease-out forwards;
}

@keyframes name-dissappear{
    from {
        opacity: 1;
        scale: 1;
    }
    to {
        opacity: 0;
        scale: 0;
    }
}

@keyframes name-appear{
    from {
        opacity: 0;
    }
    to {
        opacity: 1;
    }
}

@keyframes zoom-out{
    from{
        transform: translateX(0);
    }
    to{
        transform: translateX(-5vw);

    }
}

@keyframes zoom-in{
    from{
        transform: translateX(-5vw);
        
    }
    to{
        transform: translateX(0);
        
    }
}


@keyframes slide-right{
    from {
        scale:2;
        transform:translateY(25%);
    }
    to {
        
        scale: 1;
        transform:translateY(0);

    }
}

@keyframes slide-left{
    from {
        scale: 1;
        transform:translateY(0);

    }
    to {
        scale:2;
        transform:translateY(25%);

    }
} 
</style>