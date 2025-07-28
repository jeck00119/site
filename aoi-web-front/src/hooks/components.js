import { ref, computed } from "vue";
import { useStore } from "vuex";

export default function useComponents(moduleName) {
    const store = useStore();

    const currentComponent = ref(null);

    const componentLoading = ref(false);
    const componentsRetrieving = ref(false);

    const components = computed(function () {
        const c = store.getters["components/getAllComponents"];
        componentsRetrieving.value = false;
        return c;
    });

    async function load(id) {
        componentLoading.value = true;

        await store.dispatch("components/loadComponent", {
            uid: id,
            type: moduleName
        });

        const component = store.getters["components/getCurrentComponent"];

        currentComponent.value = component;

        componentLoading.value = false;
    }

    function remove(id) {
        store.dispatch("components/removeComponent", {
            uid: id,
            type: moduleName
        });
        currentComponent.value = null;
    }

    async function update(component) {
        await store.dispatch("components/updateComponent", {
            type: moduleName,
            data: component
        });
    }

    function add(name) {
        store.dispatch("components/addComponent", {
            name: name,
            type: moduleName
        });
    }

    return {
        currentComponent,
        componentLoading,
        componentsRetrieving,
        components,
        load,
        remove,
        update,
        add
    }
}