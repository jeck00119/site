import { ref, computed, type Ref, type ComputedRef } from "vue";
import { useStore } from "vuex";
import type { Store } from "vuex";

export interface Component {
    uid: string;
    name: string;
    type: string;
    [key: string]: any;
}

interface ComponentsHookReturn {
    currentComponent: Ref<Component | null>;
    componentLoading: Ref<boolean>;
    componentsRetrieving: Ref<boolean>;
    components: ComputedRef<Component[]>;
    load: (id: string) => Promise<void>;
    remove: (id: string) => void;
    update: (component: Component) => Promise<void>;
    add: (name: string) => void;
}

/**
 * Components Hook for managing component CRUD operations
 * 
 * @param moduleName - The module name (e.g., 'custom_component', 'algorithm')
 * @returns Hook with component management functionality
 */
export default function useComponents(moduleName: string): ComponentsHookReturn {
    const store: Store<any> = useStore();

    const currentComponent: Ref<Component | null> = ref(null);
    const componentLoading: Ref<boolean> = ref(false);
    const componentsRetrieving: Ref<boolean> = ref(false);

    const components: ComputedRef<Component[]> = computed(() => {
        const c = store.getters["components/getAllComponents"];
        componentsRetrieving.value = false;
        return c || [];
    });

    /**
     * Load a specific component by ID
     */
    async function load(id: string): Promise<void> {
        componentLoading.value = true;

        try {
            await store.dispatch("components/loadComponent", {
                uid: id,
                type: moduleName
            });

            const component = store.getters["components/getCurrentComponent"];
            currentComponent.value = component;
        } catch (error) {
            console.error(`Failed to load component ${id}:`, error);
            throw error;
        } finally {
            componentLoading.value = false;
        }
    }

    /**
     * Remove a component by ID
     */
    function remove(id: string): void {
        store.dispatch("components/removeComponent", {
            uid: id,
            type: moduleName
        });
        currentComponent.value = null;
    }

    /**
     * Update an existing component
     */
    async function update(component: Component): Promise<void> {
        await store.dispatch("components/updateComponent", {
            type: moduleName,
            data: component
        });
    }

    /**
     * Add a new component
     */
    function add(name: string): void {
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
    };
}