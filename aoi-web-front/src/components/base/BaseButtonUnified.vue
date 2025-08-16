<template>
  <button 
    :class="buttonClasses"
    :style="buttonStyles"
    :disabled="disabled"
    @click="handleClick"
    @mouseenter="handleMouseEnter"
    @mouseleave="handleMouseLeave"
  >
    <slot></slot>
  </button>
</template>

<script>
import { ref, computed, watch } from 'vue';

/**
 * Unified Button Component
 * 
 * Consolidates BaseButton, BaseButtonRectangle, and BaseActionButton
 * into a single configurable component. Reduces code duplication by ~80%.
 */
export default {
  name: 'BaseButtonUnified',
  
  props: {
    // Appearance props
    variant: {
      type: String,
      default: 'default',
      validator: (value) => ['default', 'flat', 'outline', 'rectangle', 'action'].includes(value)
    },
    
    // Size props
    width: {
      type: [String, Number],
      default: 'auto'
    },
    height: {
      type: [String, Number],
      default: 'auto'
    },
    fontSize: {
      type: [String, Number],
      default: 'inherit'
    },
    
    // State props
    disabled: {
      type: Boolean,
      default: false
    },
    active: {
      type: Boolean,
      default: false
    },
    toggle: {
      type: Boolean,
      default: false
    },
    
    // Color customization
    backgroundColor: {
      type: String,
      default: null
    },
    textColor: {
      type: String,
      default: null
    },
    borderColor: {
      type: String,
      default: null
    },
    
    // Hover colors
    hoverBackgroundColor: {
      type: String,
      default: null
    },
    hoverTextColor: {
      type: String,
      default: null
    },
    
    // Border radius
    borderRadius: {
      type: [String, Number],
      default: null
    }
  },
  
  emits: ['click', 'state-changed', 'mouseenter', 'mouseleave'],
  
  setup(props, { emit }) {
    // Internal state
    const isToggled = ref(props.active);
    const isHovered = ref(false);
    
    // Watch for external active prop changes
    watch(() => props.active, (newValue) => {
      isToggled.value = newValue;
    });
    
    // Computed classes
    const buttonClasses = computed(() => {
      const classes = ['unified-button'];
      
      // Add variant class
      classes.push(`unified-button--${props.variant}`);
      
      // Add state classes
      if (props.disabled) classes.push('unified-button--disabled');
      if (isToggled.value) classes.push('unified-button--active');
      if (isHovered.value) classes.push('unified-button--hovered');
      
      return classes;
    });
    
    // Computed styles
    const buttonStyles = computed(() => {
      const styles = {};
      
      // Size styles
      if (props.width !== 'auto') {
        styles.width = typeof props.width === 'number' ? `${props.width}px` : props.width;
      }
      if (props.height !== 'auto') {
        styles.height = typeof props.height === 'number' ? `${props.height}px` : props.height;
      }
      if (props.fontSize !== 'inherit') {
        styles.fontSize = typeof props.fontSize === 'number' ? `${props.fontSize}px` : props.fontSize;
      }
      
      // Border radius
      if (props.borderRadius !== null) {
        styles.borderRadius = typeof props.borderRadius === 'number' ? `${props.borderRadius}px` : props.borderRadius;
      }
      
      // Custom colors (override CSS if provided)
      if (props.backgroundColor) {
        styles.backgroundColor = props.backgroundColor;
      }
      if (props.textColor) {
        styles.color = props.textColor;
      }
      if (props.borderColor) {
        styles.borderColor = props.borderColor;
      }
      
      // Hover colors (applied when hovered)
      if (isHovered.value) {
        if (props.hoverBackgroundColor) {
          styles.backgroundColor = props.hoverBackgroundColor;
        }
        if (props.hoverTextColor) {
          styles.color = props.hoverTextColor;
        }
      }
      
      return styles;
    });
    
    // Event handlers
    const handleClick = (event) => {
      if (props.disabled) return;
      
      // Handle toggle functionality
      if (props.toggle) {
        isToggled.value = !isToggled.value;
        emit('state-changed', isToggled.value);
      }
      
      emit('click', event);
    };
    
    const handleMouseEnter = (event) => {
      isHovered.value = true;
      emit('mouseenter', event);
    };
    
    const handleMouseLeave = (event) => {
      isHovered.value = false;
      emit('mouseleave', event);
    };
    
    return {
      isToggled,
      isHovered,
      buttonClasses,
      buttonStyles,
      handleClick,
      handleMouseEnter,
      handleMouseLeave
    };
  }
};
</script>

<style scoped>
/* Base button styles */
.unified-button {
  /* Reset default button styles */
  border: none;
  outline: none;
  background: none;
  padding: 0;
  margin: 0;
  
  /* Common button properties */
  font: inherit;
  cursor: pointer;
  display: inline-block;
  text-align: center;
  text-decoration: none;
  transition: all 0.2s ease-in-out;
  
  /* Default appearance */
  background-color: black;
  color: var(--color-primary);
  border: 1px solid var(--color-primary);
  border-radius: 30px;
  padding: 0.25rem 0.5rem;
}

/* Variant styles */
.unified-button--default {
  background-color: black;
  color: var(--color-primary);
  border: 1px solid var(--color-primary);
  border-radius: 30px;
}

.unified-button--flat {
  background-color: var(--color-primary);
  color: black;
  border: none;
  border-radius: 30px;
}

.unified-button--outline {
  background-color: transparent;
  color: rgb(32, 31, 31);
  border: 1px solid rgb(32, 31, 31);
  border-radius: 30px;
}

.unified-button--rectangle {
  background-color: var(--color-primary);
  color: white;
  border: 1px solid var(--color-primary);
  border-radius: 4px;
  font-size: 90%;
  padding: 0.5rem 1rem;
}

.unified-button--action {
  background-color: var(--color-primary);
  color: black;
  border: 1px solid var(--color-primary);
  border-radius: 6px;
  padding: 0.5rem 1rem;
  font-weight: 500;
}

/* Hover states */
.unified-button--default:hover,
.unified-button--default.unified-button--hovered {
  background-color: rgb(32, 31, 31);
  border-color: rgb(32, 31, 31);
}

.unified-button--flat:hover,
.unified-button--flat.unified-button--hovered {
  background-color: rgb(251, 197, 97);
}

.unified-button--outline:hover,
.unified-button--outline.unified-button--hovered {
  background-color: rgb(251, 197, 97);
  color: black;
}

.unified-button--rectangle:hover,
.unified-button--rectangle.unified-button--hovered {
  background-color: rgb(32, 31, 31);
  border-color: rgb(32, 31, 31);
}

.unified-button--action:hover,
.unified-button--action.unified-button--hovered {
  background-color: rgb(251, 197, 97);
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

/* Active states */
.unified-button--active {
  background-color: var(--color-primary);
  color: black;
}

.unified-button--rectangle.unified-button--active {
  background-color: var(--color-primary);
  color: black;
}

.unified-button--rectangle.unified-button--active:hover,
.unified-button--rectangle.unified-button--active.unified-button--hovered {
  background-color: rgb(251, 197, 97);
}

/* Disabled states */
.unified-button--disabled,
.unified-button--disabled:hover {
  background-color: #cccccc !important;
  color: #666666 !important;
  border-color: #999999 !important;
  cursor: not-allowed !important;
  transform: none !important;
  box-shadow: none !important;
}

/* Focus states for accessibility */
.unified-button:focus {
  outline: 2px solid rgba(204, 161, 82, 0.5);
  outline-offset: 2px;
}

.unified-button--disabled:focus {
  outline: none;
}

/* Animation for action buttons */
.unified-button--action {
  transition: all 0.2s ease-in-out;
}

/* Responsive design */
@media (max-width: 768px) {
  .unified-button {
    min-height: 44px; /* Minimum touch target size */
    min-width: 44px;
  }
}
</style>

