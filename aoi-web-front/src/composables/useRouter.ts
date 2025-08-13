/**
 * Router Composable for Centralized Navigation and Auth Guards
 * 
 * Provides centralized routing logic with authentication and authorization checks
 */

import { computed } from 'vue';
import { useRouter as useVueRouter, useRoute } from 'vue-router';
import type { Router, RouteLocationNormalized, NavigationGuardNext } from 'vue-router';
import { useAuthStore } from './useStore';

/**
 * Enhanced router composable with auth integration
 */
export function useRouter() {
  const router: Router = useVueRouter();
  const route = useRoute();

  // Current route info
  const currentPath = computed(() => route.path);
  const currentRoute = computed(() => route);
  const routeParams = computed(() => route.params);
  const routeQuery = computed(() => route.query);

  /**
   * Navigate with error handling
   * @param path - Path to navigate to
   * @param replace - Whether to replace current route
   */
  const navigateTo = async (path: string, replace: boolean = false) => {
    try {
      if (replace) {
        await router.replace(path);
      } else {
        await router.push(path);
      }
    } catch (error) {
      console.error('Navigation error:', error);
      throw error;
    }
  };

  /**
   * Redirect to login
   */
  const redirectToLogin = async () => {
    await navigateTo('/login', true);
  };

  /**
   * Go back in history
   */
  const goBack = () => {
    router.go(-1);
  };

  /**
   * Go forward in history  
   */
  const goForward = () => {
    router.go(1);
  };

  /**
   * Replace current route
   * @param path - Path to replace with
   */
  const replaceCurrent = async (path: string) => {
    await navigateTo(path, true);
  };

  /**
   * Check if current route requires auth
   */
  const requiresAuth = computed(() => route.meta.requiresAuth === true);

  /**
   * Check if current route requires admin
   */
  const requiresAdmin = computed(() => route.meta.requiresAdmin === true);

  /**
   * Check if current route requires unauthenticated user
   */
  const requiresUnauth = computed(() => route.meta.requiresUnauth === true);

  /**
   * Get breadcrumbs for current route
   */
  const breadcrumbs = computed(() => {
    const matched = route.matched.filter(record => record.meta?.breadcrumb);
    return matched.map(record => ({
      text: record.meta.breadcrumb,
      path: record.path,
      active: record.path === route.path
    }));
  });

  return {
    // Vue Router
    router,
    route,
    currentPath,
    currentRoute,
    routeParams,
    routeQuery,

    // Route checks
    requiresAuth,
    requiresAdmin,
    requiresUnauth,

    // Navigation methods
    navigateTo,
    redirectToLogin,
    goBack,
    goForward,
    replaceCurrent,
    breadcrumbs
  };
}

/**
 * Route Guards for Authentication
 */
export function useRouteGuards() {
  /**
   * Authentication guard
   * @param to - Route being navigated to
   * @param from - Route being navigated from  
   * @param next - Navigation guard callback
   */
  const authGuard = async (to: RouteLocationNormalized, from: RouteLocationNormalized, next: NavigationGuardNext) => {
    const authStore = useAuthStore();
    const { isAuthenticated, currentUser, userLevel } = authStore;
    
    console.log('Auth Guard Check for route:', to.path);
    console.log('User authenticated:', isAuthenticated.value);
    console.log('Current user:', currentUser.value);
    console.log('User level:', userLevel.value);
    console.log('Route meta:', to.meta);
    
    // Routes that require authentication
    if (to.meta.requiresAuth) {
      if (!isAuthenticated.value) {
        console.log('Auth required but user not authenticated, redirecting to login');
        next('/login');
        return;
      }
    }
    
    // Routes that require admin access
    if (to.meta.requiresAdmin) {
      if (!isAuthenticated.value) {
        console.log('Admin access required but user not authenticated, redirecting to login');
        next('/login');
        return;
      }
      
      if (userLevel.value !== 'admin') {
        console.log('Admin access required but user level is:', userLevel.value, 'currentUser:', currentUser.value);
        next('/aoi');
        return;
      }
    }
    
    // Routes that require unauthenticated user (login, signup)
    if (to.meta.requiresUnauth) {
      if (isAuthenticated.value) {
        console.log('User already authenticated, redirecting to configurations');
        next('/configurations');
        return;
      }
    }
    
    // Default behavior - allow navigation
    next();
  };
  
  return {
    authGuard
  };
}

// Export for use in router configuration
export default useRouter;