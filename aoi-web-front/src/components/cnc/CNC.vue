<template>
  <div class="cnc-container">
    <div class="wrapper">
      <div class="positions-grid">
        <div class="axis-info">
          <h3>Axis: {{ uAxisName }}</h3>
        </div>

        <div class="col-container">
          <div class="axis">
            <div>Axis</div>
            <div>x</div>
            <div>Y</div>
            <div>Z</div>
          </div>

          <div class="position">
            <div>Position</div>
            <div class="boxed">{{ pos.x.toFixed(3) }}</div>
            <div class="boxed">{{ pos.y.toFixed(3) }}</div>
            <div class="boxed">{{ pos.z.toFixed(3) }}</div>
          </div>

          <div class="m-position">
            <div>Position(M)</div>
            <div class="boxed">{{ mPos.x.toFixed(3) }}</div>
            <div class="boxed">{{ mPos.y.toFixed(3) }}</div>
            <div class="boxed">{{ mPos.z.toFixed(3) }}</div>
          </div>

          <div class="w-position">
            <div>Position(W)</div>
            <div class="boxed">{{ wPos.x.toFixed(3) }}</div>
            <div class="boxed">{{ wPos.y.toFixed(3) }}</div>
            <div class="boxed">{{ wPos.z.toFixed(3) }}</div>
          </div>
        </div>
      </div>
      <div class="save-grid">
        <div class="action-general">
          <button
            class="button-save"
            id="?"
            @click="openLocationDeleteDialog"
          >
            <div class="button-container">
                <div class="button-icon">
                  <font-awesome-icon icon="trash" />
                </div>
            </div>
          </button>
          <button
            class="button-save"
            id="savePos"
            @click="openSaveLocationDialog('all')"
          >
          <div class="button-container">
              <div class="button-icon">
                <font-awesome-icon icon="floppy-disk" />
              </div>
          </div>
          </button>
        </div>
        <div class="action-axis">
          <button
            class="button-save"
            id="savePosX"
            @click="openSaveLocationDialog('x')"
          >
            <div class="button-container">
                <div class="button-icon">
                  <font-awesome-icon icon="floppy-disk" />
                </div>
                <div class="button-text">
                    X
                </div>
            </div>
          </button>
          <button
            class="button-save"
            id="savePosY"
            @click="openSaveLocationDialog('y')"
          >
            <div class="button-container">
                <div class="button-icon">
                  <font-awesome-icon icon="floppy-disk" />
                </div>
                <div class="button-text">
                    Y
                </div>
            </div>
          </button>
          <button
            class="button-save"
            id="savePosZ"
            @click="openSaveLocationDialog('z')"
          >
            <div class="button-container">
                <div class="button-icon">
                  <font-awesome-icon icon="floppy-disk" />
                </div>
                <div class="button-text">
                    Z
                </div>
            </div>
          </button>
        </div>
      </div>
      <div class="move-x-grid">
        <div>
          <div>
            <button
              class="button-up"
              id="increaseX"
              @click="increaseAxis((axis = 'x'))"
            >
              <font-awesome-icon icon="plus" />
            </button>
          </div>
          <label>X</label>
          <div>
            <button
              class="button-down"
              id="decreaseX"
              @click="decreaseAxis((axis = 'x'))"
            >
              <font-awesome-icon icon="minus" />
            </button>
          </div>
        </div>
      </div>
      <div class="move-y-grid">
        <div>
          <div>
            <button
              class="button-up"
              id="increaseY"
              @click="increaseAxis((axis = 'y'))"
            >
              <font-awesome-icon icon="plus" />
            </button>
          </div>
          <label>Y</label>
          <div>
            <button
              class="button-down"
              id="decreaseY"
              @click="decreaseAxis((axis = 'y'))"
            >
              <font-awesome-icon icon="minus" />
            </button>
          </div>
        </div>
      </div>
      <div class="move-z-grid">
        <div>
          <div>
            <button
              class="button-up"
              type="button"
              id="increaseZ"
              @click="increaseAxis((axis = 'z'))"
            >
              <font-awesome-icon icon="plus" />
            </button>
          </div>
          <label>Z</label>
          <div>
            <button
              class="button-down"
              type="button"
              id="decreaseZ"
              @click="decreaseAxis((axis = 'z'))"
            >
              <font-awesome-icon icon="minus" />
            </button>
          </div>
        </div>
      </div>
      <div class="commands-grid">
          <div class="title">
            General Commands
          </div>
          <div class="actions-container">
            <div class="flex-row">
              <button
                class="button-wide command-button"
                @click="commandCnc((command = 'home'))"
              >
                <div class="button-container">
                    <div class="button-icon">
                      <font-awesome-icon icon="home" />
                    </div>
                    <div class="button-text">
                        HOME
                    </div>
                </div>
              </button>

              <button
                id="softResetButton"
                class="button-wide command-button"
                type="button"
                @click="commandCnc((command = 'soft_reset'))"
              >
                <div class="button-container">
                    <div class="button-icon">
                      <font-awesome-icon icon="arrow-rotate-right" />
                    </div>
                    <div class="button-text">
                        SOFT RESET
                    </div>
                </div>
              </button>

              <button
                class="button-wide command-button"
                type="button"
                @click="commandCnc((command = 'unlock'))"
              >
                <div class="button-container">
                    <div class="button-icon">
                      <font-awesome-icon icon="lock-open"></font-awesome-icon>
                    </div>
                    <div class="button-text">
                        UNLOCK
                    </div>
                </div>
              </button>
            </div>
            <div class="flex-row">
              <button
                class="button-wide command-button"
                @click="commandCnc((command = 'abort'))"
              >
                <div class="button-container">
                    <div class="button-icon">
                      <font-awesome-icon icon="stop" />
                    </div>
                    <div class="button-text">
                        ABORT
                    </div>
                </div>
              </button>

              <button
                class="button-wide command-button"
                @click="commandCnc((command = 'zero_reset'))"
              >
                <div class="button-container">
                    <div class="button-icon">
                      <font-awesome-icon icon="arrows-rotate" />
                    </div>
                    <div class="button-text">
                        RESET ZERO
                    </div>
                </div>
              </button>

              <button
                class="button-wide command-button"
                type="button"
                @click="commandCnc((command = 'return_to_zero'))"
              >
                <div class="button-container">
                    <div class="button-icon">
                      <font-awesome-icon icon="arrow-rotate-left" />
                    </div>
                    <div class="button-text">
                        RETURN ZERO
                    </div>
                </div>
              </button>
            </div>
          </div>
      </div>
      <div class="locations-grid">
        <div class="title">
          Shortcuts
        </div>
        <div class="actions-container">
          <div class="flex-row">
            <button
                @click.right="getButtonFromLocationShortcut"
                @click="onLocationShortcutClick"
                oncontextmenu="event.preventDefault();"
                class="button-wide custom-loc-button"
                type="button"
              ></button>
              <button
                @click.right="getButtonFromLocationShortcut"
                @click="onLocationShortcutClick"
                oncontextmenu="event.preventDefault();"
                class="button-wide custom-loc-button"
                type="button"
              ></button>
              <button
                @click.right="getButtonFromLocationShortcut"
                @click="onLocationShortcutClick"
                oncontextmenu="event.preventDefault();"
                class="button-wide custom-loc-button"
                type="button"
              ></button>
          </div>
          <div class="flex-row">
            <button
                @click.right="getButtonFromLocationShortcut"
                @click="onLocationShortcutClick"
                oncontextmenu="event.preventDefault();"
                class="button-wide custom-loc-button"
                type="button"
              ></button>
              <button
                @click.right="getButtonFromLocationShortcut"
                @click="onLocationShortcutClick"
                oncontextmenu="event.preventDefault();"
                class="button-wide custom-loc-button"
                type="button"
              ></button>
              <button
                @click.right="getButtonFromLocationShortcut"
                @click="onLocationShortcutClick"
                oncontextmenu="event.preventDefault();"
                class="button-wide custom-loc-button"
                type="button"
              ></button>
          </div>
          <div class="flex-row">
            <button
                @click.right="getButtonFromLocationShortcut"
                @click="onLocationShortcutClick"
                oncontextmenu="event.preventDefault();"
                class="button-wide custom-loc-button"
                type="button"
              ></button>
              <button
                @click.right="getButtonFromLocationShortcut"
                @click="onLocationShortcutClick"
                oncontextmenu="event.preventDefault();"
                class="button-wide custom-loc-button"
                type="button"
              ></button>
              <button
                @click.right="getButtonFromLocationShortcut"
                @click="onLocationShortcutClick"
                oncontextmenu="event.preventDefault();"
                class="button-wide custom-loc-button"
                type="button"
              ></button>
          </div>
        </div>
      </div>
      <div class="feedrate-grid">
        <div class="state-wrapper">
          <div class="state">State: {{ cncState }}</div>
          <div class="connection-status">
            {{ webSocketState }}
            <button 
              class="button-websocket"
              @click="reconnectToWs"
            >
              <div><font-awesome-icon icon="arrows-rotate" /></div>
            </button>
          </div>
        </div>
        <div class="feedrate-section">
          <div class="feedrate-control">
            <div class="feedrate-label">Feedrate:</div>
            <div class="feedrate-input">
              <input
                id="feedrate"
                type="number"
                min="1"
                step="1"
                v-model="selectedFeedrate"
              />
            </div>
          </div>
          <div class="feedrate-info">
            <div class="max-feedrate-label">
              Max X/Y/Z feedrate:
            </div>
            <div class="max-feedrate-val">
              -
            </div>
          </div>
        </div>
      </div>
      <div class="steps-grid">
        <div class="title">
          Steps
        </div>
        <div class="actions-container">
          <div class="flex-row">
            <div class="form-control">
              <input type="radio" value="1" id="1" v-model="selectedSteps" />
              <label for="1">1</label>
            </div>
            <div class="form-control">
              <input type="radio" value="5" id="5" v-model="selectedSteps" />
              <label for="5">5</label>
            </div>
            <div class="form-control">
              <input type="radio" value="10" id="10" v-model="selectedSteps" />
              <label for="10">10</label>
            </div>
            <div class="form-control">
              <input type="radio" value="20" id="20" v-model="selectedSteps" />
              <label for="20">20</label>
            </div>
          </div>
          <div class="flex-row">
            <div class="form-control">
              <input type="radio" value="30" id="30" v-model="selectedSteps" />
              <label for="30">30</label>
            </div>
            <div class="form-control">
              <input type="radio" value="50" id="50" v-model="selectedSteps" />
              <label for="50">50</label>
            </div>
            <div class="form-control">
              <input type="radio" value="100" id="100" v-model="selectedSteps" />
              <label for="100">100</label>
            </div>
            <div class="form-control">
              <input type="radio" value="200" id="200" v-model="selectedSteps" />
              <label for="200">200</label>
            </div>
          </div>
          <div class="flex-row">
            <div class="form-control spaced">
              <label for="custom">Value:</label>
              <input type="number" id="custom" v-model="selectedSteps" />
            </div>
          </div>
        </div>
      </div>
      <div class="terminal-grid">
        <label>UGS Terminal</label>
        <textarea readonly v-model="ugsTerminalHistory"></textarea>
        <div class="terminal-control">
          <input
            type="text"
            v-model="usgCommandLine"
            @keyup.enter="ugsTerminalSend"
            class="terminal-input"
          />
          <button
            @click="ugsTerminalSend"
            class="button-wide small-button"
          >
            <v-icon name="io-send-sharp" scale="0.7"/>
          </button>
        </div>
      </div>
    </div>
    <base-dialog
      title="Choose CNC Location:"
      :show="showButtonLocationDialog"
      @close="closeShortcutDialog"
    >
      <template #default>
        <div class="form-control-dialog">
          <select class="dropdown" v-model="selectedLocation">
            <option
              v-for="loc in locations"
              :key="loc.uid"
              :value="loc"
            >
              {{ loc.name }}
            </option>
          </select>
          <label>New Location Name: </label>
          <input type="text" class="location-name" v-model="renamedLocation" />
        </div>
      </template>
      <template #actions>
        <div class="action-control">
          <base-button width="7vw" mode="flat" @click="attachLocationClick">
            Attach
          </base-button>
          <base-button width="7vw" mode="flat" @click="renameLocationClick">
            Rename
          </base-button>
          <base-button width="7vw" mode="flat" @click="clearLocationClick">
            Clear
          </base-button>
        </div>
      </template>
    </base-dialog>

    <base-dialog
      title="Save new location"
      :show="showSaveLocationDialog"
      @close="closeSaveLocationDialog"
    >
      <label>Name:</label> <input type="text" v-model.trim="newLocationName" />
      <p>New position coordinates</p>
      <table>
        <thead>
          <tr>
            <th>X</th>
            <th>Y</th>
            <th>Z</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>
              <div class="boxed">{{ pos.x.toFixed(3) }}</div>
            </td>
            <td>
              <div class="boxed">{{ pos.y.toFixed(3) }}</div>
            </td>
            <td>
              <div class="boxed">{{ pos.z.toFixed(3) }}</div>
            </td>
          </tr>
        </tbody>
      </table>
      <base-button @click="saveLocation">Save</base-button>
      <base-button>Cancel</base-button>
    </base-dialog>

    <base-dialog
      title="Delete CNC Location:"
      :show="showLocationDeleteDialog"
      @close="closeLocationDeleteDialog"
    >
      <template #default>
        <div class="form-control-dialog">
          <select class="dropdown" v-model="selectedLocationForDelete">
            <option v-for="loc in locations" :key="loc" v-bind:value="loc.uid">
              {{ loc.name }}
            </option>
          </select>
        </div>
      </template>
      <template #actions>
        <div class="action-control">
          <base-button width="7vw" mode="flat" @click="deleteLocation">
            Delete
          </base-button>
        </div>
      </template>
    </base-dialog>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted, computed } from "vue";
import { useStore } from "vuex";
import api from "../../utils/api.js";

export default {
  props: ["axisName", "axisUid"],
  setup(props, context) {
    const store = useStore();

    const selectedFeedrate = ref(100);
    const selectedSteps = ref(1);

    const usgCommandLine = ref("");
    const ugsTerminalHistory = ref("");

    let shortcutButtonClicked = null;
    let shortcutLocationName = null;

    const showButtonLocationDialog = ref(false);
    const showSaveLocationDialog = ref(false);
    const showLocationDeleteDialog = ref(false);

    const selectedLocationForDelete = ref("");
    const selectedLocation = ref(null);
    const renamedLocation = ref("");
    const newLocationName = ref("");

    const webSocketState = ref("");

    let socket = null;
    let newLocationSaveType = null;

    function getButtonFromLocationShortcut(e) {
      shortcutButtonClicked = e.target ? e.target : e.srcElement;
      openShortcutDialog();
    }

    function onLocationShortcutClick(e) {
      if (e.srcElement.id) {
        store.dispatch("cnc/api_moveToLocation", {
          cncUid: props.axisUid,
          location: e.srcElement.id,
          timeout: 5,
          block: false,
        });
      }
    }

    onMounted(() => {
      store.dispatch("cnc/addPositionData", {
        uid: props.axisUid
      });

      connectToWs();
      store.dispatch("cnc/fetchLocations", props.axisUid);
    });

    onUnmounted(() => {
      disconnectFromWs();
    });

    function ugsTerminalSend() {
      usgCommandLine.value = usgCommandLine.value.trim();

      if (usgCommandLine.value == "clear") {
        ugsTerminalHistory.value = "";
        usgCommandLine.value = "";
      }

      if (usgCommandLine.value != "") {
        ugsTerminalHistory.value += `>> ${usgCommandLine.value}\n`;
        store.dispatch("cnc/api_terminal", {
          cncUid: props.axisUid,
          command: usgCommandLine.value,
        });
        usgCommandLine.value = "";
      }
    }

    function closeShortcutDialog() {
      showButtonLocationDialog.value = false;
    }

    function openShortcutDialog() {
      renamedLocation.value = ''
      showButtonLocationDialog.value = true;
    }

    function selectShortcutName(e) {
      shortcutLocationName = e.target ? e.target : e.srcElement;
    }

    function attachLocationClick() {
      shortcutButtonClicked.innerText = selectedLocation.value.name;
      shortcutButtonClicked.id = selectedLocation.value.uid;
      closeShortcutDialog();
    }

    function renameLocationClick() {
      if( renamedLocation.value.trim() != "")
      {
        store.dispatch("cnc/patchLocation", {locationUid:selectedLocation.value.uid, newName: renamedLocation.value})
        setTimeout(() => {
          store.dispatch("cnc/fetchLocations", props.axisUid);
        }, 300);
      }
    }

    function clearLocationClick() {
      shortcutButtonClicked.innerText = "";
      closeShortcutDialog();
    }

    function openSaveLocationDialog(type) {
      newLocationSaveType = type;
      showSaveLocationDialog.value = true;
    }

    function closeSaveLocationDialog() {
      showSaveLocationDialog.value = false;
    }

    function openLocationDeleteDialog() {
      showLocationDeleteDialog.value = true;
    }

    function closeLocationDeleteDialog() {
      showLocationDeleteDialog.value = false;
    }

    function deleteLocation() {
      store.dispatch("cnc/deleteLocation", selectedLocationForDelete.value);

      setTimeout(() => {
        store.dispatch("cnc/fetchLocations", props.axisUid);
      }, 300);
      selectedLocationForDelete.value = "";
    }

    function saveLocation() {
      store.dispatch("cnc/postLocation", [
        {
          uid: "str",
          axisUid: props.axisUid,
          degreeInStep: "deg",
          feedrate: selectedFeedrate.value,
          name: newLocationName.value,
          x: "x",
          y: "y",
          z: "z",
        },
        newLocationSaveType,
        props.axisUid
      ]);
      newLocationName.value = "";

      setTimeout(() => {
        store.dispatch("cnc/fetchLocations", props.axisUid);
      }, 200);
    }

    async function connectToWs() {
      const wsUrl = await api.getFullUrl(`/cnc/${props.axisUid}/ws`);
      socket = new WebSocket(wsUrl.replace('http:', 'ws:'));

      socket.addEventListener("open", onCncSocketOpen);
      socket.addEventListener("close", onCncSocketClose);
      socket.addEventListener("error", onCncSocketError);
      socket.addEventListener("message", onCncSocketMsgRecv);
    }

    function reconnectToWs() {
      disconnectFromWs();
      connectToWs();
    }

    async function disconnectFromWs() {
      await store.dispatch("cnc/closeStateSocket", {
        uid: props.axisUid
      });

      if(socket) {
        socket.removeEventListener("open", onCncSocketOpen);
        socket.removeEventListener("close", onCncSocketClose);
        socket.removeEventListener("error", onCncSocketError);
        socket.removeEventListener("message", onCncSocketMsgRecv);

        socket.close();
        socket = null;
      }
    }

    function onCncSocketOpen() {
      webSocketState.value = "Open";
      if (socket) socket.send("eses");
    }

    function onCncSocketMsgRecv(event) {
      let msg = JSON.parse(event.data);
      handleSingleMessage(msg);
    }

    function handleSingleMessage(msg) {
      switch (msg.event) {
        case "on_stateupdate":
          store.dispatch("cnc/setMPos",{
            uid: props.axisUid,
            x: msg.mPos[0],
            y: msg.mPos[1],
            z: msg.mPos[2]
          });

          store.dispatch("cnc/setWPos", {
            uid: props.axisUid,
            x: msg.wPos[0],
            y: msg.wPos[1],
            z: msg.wPos[2]
          });

          store.dispatch("cnc/setPos", {
            uid: props.axisUid
          });

          store.dispatch("cnc/setCNCState", {
            uid: props.axisUid,
            state: msg.state
          });
          break;

        case "on_idle":
          store.dispatch("cnc/setCNCState", {
            uid: props.axisUid,
            state: msg.message
          });
          break;

        case "on_read":
          addToConsole(msg.message);
          break;

        case "batch":
          // Handle batched messages
          if (msg.messages && Array.isArray(msg.messages)) {
            msg.messages.forEach(batchedMsg => {
              handleSingleMessage(batchedMsg);
            });
          }
          break;

        case "on_settings_downloaded":
          for (const prop in msg.message) {
            ugsTerminalHistory.value += `>> $${prop} = ${msg.message[prop].val}\n`;
          }
          break;

        case "on_error":
          ugsTerminalHistory.value += `Error:${msg.message}`;
          break;
        }
    }

    function onCncSocketClose() {
      webSocketState.value = "close";
    }

    function onCncSocketError() {
      webSocketState.value = "error";
    }

    function commandCnc(command) {
      store.dispatch("cnc/api_command", {
        cncUid: props.axisUid,
        command: command,
      });
    }

    function increaseAxisCnc(axis) {
      store.dispatch("cnc/api_increaseAxis", {
        cncUid: props.axisUid,
        axis: axis,
        step: selectedSteps.value,
        feedrate: selectedFeedrate.value,
      });
    }

    function decreaseAxisCnc(axis) {
      store.dispatch("cnc/api_decreaseAxis", {
        cncUid: props.axisUid,
        axis: axis,
        step: selectedSteps.value,
        feedrate: selectedFeedrate.value,
      });
    }
    
    const pos = computed(() => store.getters["cnc/pos"](props.axisUid));

    return {
      uAxisName: props.axisName,
      getButtonFromLocationShortcut,
      ugsTerminalSend,
      ugsTerminalHistory,
      usgCommandLine,
      openShortcutDialog,
      closeShortcutDialog,
      showButtonLocationDialog,
      showSaveLocationDialog,
      showLocationDeleteDialog,
      selectedLocationForDelete,
      openLocationDeleteDialog,
      closeLocationDeleteDialog,
      deleteLocation,
      openSaveLocationDialog,
      closeSaveLocationDialog,
      attachLocationClick,
      renameLocationClick,
      clearLocationClick,
      selectedLocation,
      renamedLocation,
      selectedFeedrate,
      newLocationName,
      webSocketState,
      saveLocation,
      selectShortcutName,
      commandCnc,
      onLocationShortcutClick,
      reconnectToWs,
      locations: computed(() => store.getters["cnc/locations"]),
      mPos: computed(() => store.getters["cnc/mPos"](props.axisUid)),
      wPos: computed(() => store.getters["cnc/wPos"](props.axisUid)),
      pos,
      cncState: computed(() => {
        const state = store.getters["cnc/cncState"](props.axisUid);
        return state ? state.toUpperCase() : state;
      }),
      increaseAxis: increaseAxisCnc,
      decreaseAxis: decreaseAxisCnc,
      selectedSteps,
    };
  },
};
</script>

<style scoped>
.cnc-container {
  margin: 1rem 1rem;
  width: 100%;
  border-radius: 12px;
  box-shadow: 0 2px 8px black;
  padding: 0.5rem;
  text-align: center;
  background-color: #515151;
  font-family: "Droid Serif";
  font-size: 1rem;
  font-weight: 700;
  display: flex;
}

.wrapper {
  display: grid;
  align-content: normal;
  gap: 5px;
  width: 100%;
}

.positions-grid {
  grid-column: 1/5;
  grid-row: 2/5;
  color: white;
  background-color: #161616;
  display: flex;
  flex-direction: column;
  width: 100%;
  height: 100%;
  justify-content: space-around;
  margin: auto;
}

.col-container {
  display: flex;
  justify-content: center;
  width: 95%;
  margin: 0 auto;
}

.axis {
  display: flex;
  flex-direction: column;
  width: 50%;
  flex-grow: 1;
  height: 100%;
}

.position {
  display: flex;
  flex-direction: column;
  width: 100%;
  flex-grow: 2;
  height: 100%;
}

.m-position {
  display: flex;
  flex-direction: column;
  width: 100%;
  flex-grow: 2;
}

.w-position {
  display: flex;
  flex-direction: column;
  width: 100%;
  flex-grow: 2;
}

textarea {
  background-color: black;
  color: white;
  width: 100%;
  height: 100%;
}

.form-control-dialog {
  display: flex;
  background-color: inherit;
  border: none;
  color: white;
  justify-content: center;
  flex-direction: column;
  align-items: center;
}

.boxed {
  height: 100%;
  width: 100%;
  background-color: rgb(41, 41, 41);
}

button {
  background: rgb(41, 41, 41);
  color: #ffffff;
}

.button-wide {
  border-radius: 20px;
  box-shadow: rgb(41, 41, 41) 0 3px 5px -3px;
  box-sizing: border-box;
  cursor: pointer;
  border: 0;
  font-size: 0.8rem;
  height: 100%;
  margin: 3px;
}

.button-wide:hover {
  box-shadow: rgba(255, 255, 255, 0.2) 0 3px 15px inset,
    rgba(0, 0, 0, 0.1) 0 3px 5px, rgba(0, 0, 0, 0.1) 0 10px 13px;
  transform: scale(1.05);
}

.command-button {
  width: 33%;
  height: 5vh;
}

.custom-loc-button {
  width: 33%;
  height: 3.5vh;
}

.button-save {
  width: 40%;
  height: 50px;
  margin-bottom: 2%;
}

.button-save:hover {
  border: 1px solid rgb(61, 59, 59);
}

.button-down {
  width: 100%;
  height: 60px;
  border-top-left-radius: 0;
  border-top-right-radius: 0;
  margin: 1%;
}

.button-down:hover {
  border: 1px solid rgb(61, 59, 59);
}

.button-up {
  width: 100%;
  height: 60px;
  border-bottom-right-radius: 0;
  border-bottom-left-radius: 0;
  margin: 1%;
}

.button-up:hover {
  border: 1px solid rgb(61, 59, 59);
}

.dropdown {
  width: 60%;
  height: 30px;
  margin-bottom: 10px;
  background-color: rgb(204, 161, 82);
  color: rgb(0, 0, 0);
}

.location-name {
  width: 60%;
  height: 30px;
  margin-top: 10px;
}

input {
  background-color: rgb(41, 41, 41);
  border: none;
  color: white;
  text-align: center;
}

.save-grid {
  color: white;
  grid-column: 1;
  grid-row: 5/8;
  background-color: #161616;
  justify-content: space-evenly;
  align-items: center;
  display: flex;
  flex-direction: column;
  width: 100%;
  height: 100%;
}

.action-general {
  display: flex;
  width: 100%;
  justify-content: space-around;
}

.action-axis {
  width: 100%;
  display: flex;
  flex-wrap: wrap;
  justify-content: space-around;
}

.move-x-grid {
  color: white;
  grid-column: 2;
  grid-row: 5/8;
  background-color: #161616;
  justify-content: center;
  align-items: center;
  display: grid;
}

.move-y-grid {
  color: white;
  grid-column: 3;
  grid-row: 5/8;
  background-color: #161616;
  justify-content: center;
  align-items: center;
  display: grid;
}

.move-z-grid {
  color: white;
  grid-column: 4;
  grid-row: 5/8;
  background-color: #161616;
  justify-content: center;
  align-items: center;
  display: grid;
}

.commands-grid {
  color: white;
  grid-column: 5/9;
  grid-row: 2/5;
  background-color: #161616;
  display: flex;
  flex-direction: column;
  justify-content: space-around;
  align-content: center;
  width: 100%;
  height: 100%;
  margin: auto;
}

.title {
  grid-column: 1/4;
  background-color: rgb(41, 41, 41);
  border-radius: 20px;
  font-size: 1.5rem;
  width: 100%;
}

.actions-container {
  display: flex;
  flex-direction: column;
  width: 100%;
}

.flex-row {
  display: flex;
  margin-bottom: 0.5%;
}

.locations-grid {
  color: white;
  grid-column: 9/14;
  grid-row: 5/8;
  background-color: #161616;
  justify-content: center;
  align-items: center;
  display: flex;
  flex-direction: column;
  justify-content: space-around;
}

.feedrate-grid {
  color: white;
  grid-column: 9/14;
  grid-row: 2/5;
  background-color: #161616;
  justify-content: space-around;
  align-items: center;
  display: flex;
  flex-direction: column;
  width: 100%;
}

.state-wrapper {
  display: flex;
  width: 100%;
}

.state {
  display: flex;
  width: 60%;
  justify-content: flex-start;
  margin-left: 10%;
  font-size: 1.5rem;
}

.connection-status {
  display: flex;
  width: 30%;
  justify-content: space-around;
  align-items: center;
  font-size: 0.7rem;
}

.feedrate-section {
  margin-top: 1vh;
  display: flex;
  flex-direction: column;
  width: 100%;
}

.feedrate-control {
  display: flex;
  justify-content: space-around;
}

.feedrate-info {
  display: flex;
  justify-content: space-around;
}

.feedrate-label {
  width: 40%;
  margin-left: 10%;
  display: flex;
  justify-content: flex-start;
}

.feedrate-input {
  width: 50%;
}

#feedrate {
  width: 90%;
}

.max-feedrate-label {
  width: 40%;
  margin-left: 10%;
  display: flex;
  justify-content: flex-start;
  font-size: 0.9rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.max-feedrate-val {
  width: 50%;
}

.button-websocket {
  background-color: inherit;
}

.steps-grid {
  color: white;
  grid-column: 5/9;
  grid-row: 5/8;
  background-color: #161616;
  justify-content: space-around;
  align-items: center;
  display: flex;
  flex-direction: column;
}

.form-control {
  display: flex;
  flex-direction: row;
  background-color: inherit;
  border: none;
  color: white;
  justify-content: center;
}

.spaced {
  justify-content: space-between;
  width: 90%;
  margin: auto;
}

.terminal-grid {
  color: white;
  grid-column: 14/17;
  grid-row: 2/8;
  background-color: #161616;
  display: flex;
  flex-direction: column;
}

.terminal-control {
  display: flex;
  width: 100%;
  align-items: center;
}

.terminal-input {
  width: 100%;
  height: 95%;
  text-align: left;
}

select {
  text-align: center;
  text-align-last: center;
  -moz-text-align-last: center;
}

.button-container {
    display: flex;
    width: 100%;
    justify-content: space-evenly;
    align-items: center;
}

.button-icon {
    display: flex;
    justify-content: center;
    align-items: center;
}

.button-text {
    display: flex;
    justify-content: center;
    align-items: center;
}

@media screen and (max-width: 1300px) and (min-width: 951px) {
  .feedrate-grid {
    color: white;
    grid-column: 1/5;
    grid-row: 8/11;
    background-color: #161616;
    justify-content: space-around;
    align-items: center;
    display: flex;
    flex-direction: column;
  }

  .locations-grid {
    color: white;
    grid-column: 5/9;
    grid-row: 8/11;
    background-color: #161616;
    justify-content: center;
    align-items: center;
    display: flex;
    flex-direction: column;
    justify-content: space-around;
    width: 100%;
  }

  .terminal-grid {
    color: white;
    grid-column: 9/13;
    grid-row: 2/11;
    background-color: #161616;
    display: flex;
    flex-direction: column;
  }
}

@media screen and (max-width: 950px) {
  .feedrate-grid {
    color: white;
    grid-column: 1/5;
    grid-row: 8/11;
    background-color: #161616;
    justify-content: space-around;
    align-items: center;
    display: flex;
    flex-direction: column;
  }

  .locations-grid {
    color: white;
    grid-column: 5/9;
    grid-row: 8/11;
    background-color: #161616;
    justify-content: center;
    align-items: center;
    display: flex;
    flex-direction: column;
    justify-content: space-around;
    width: 100%;
  }

  .terminal-grid {
    color: white;
    grid-column: 1/9;
    grid-row: 11/12;
    background-color: #161616;
    display: flex;
    flex-direction: column;
  }
}

@keyframes moveInLeft {
  0% {
    opacity: 0;
    transform: translateY(150px);
  }
  100% {
    opacity: 1;
    transform: translateY(0px);
  }
}
</style>