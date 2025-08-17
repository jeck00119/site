/**
 * Router Composable for Centralized Navigation and Auth Guards
 * 
 * Provides centralized routing logic with authentication and authorization checks
 */

import { computed } from 'vue';
import { useRouter as useVueRouter, useRoute } from 'vue-router';
import type { Router, RouteLocationNormalized, NavigationGuardNext } from 'vue-router';
import { useAuthStore } from './useStore';
import { logger } from '@/utils/logger';

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
      logger.error('Navigation error', error);
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
    
    // Auth guard debug logs removed to reduce log spam
    
    // Routes that require authentication
    if (to.meta.requiresAuth) {
      if (!isAuthenticated.value) {
        // Redirecting to login - debug removed
        next('/login');
        return;
      }
    }
    
    // Routes that require admin access
    if (to.meta.requiresAdmin) {
      if (!isAuthenticated.value) {
        // Admin access required, redirecting to login - debug removed
        next('/login');
        return;
      }
      
      if (userLevel.value !== 'admin') {
        // Admin access required but insufficient privileges - debug removed
        next('/aoi');
        return;
      }
    }
    
    // Routes that require unauthenticated user (login, signup)
    if (to.meta.requiresUnauth) {
      if (isAuthenticated.value) {
        // User already authenticated, redirecting - debug removed
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