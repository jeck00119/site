<template>
  <div 
    class="resizable-window"
    :style="windowStyle"
    @mousedown="startDrag"
    ref="windowElement"
  >
    <!-- Window Header for dragging -->
    <div class="window-header" @mousedown="startDrag">
      <div class="window-title">
        <slot name="title">{{ title }}</slot>
      </div>
      <div class="window-controls">
        <button @click="toggleMinimize" class="control-btn minimize-btn">
          {{ isMinimized ? '□' : '_' }}
        </button>
      </div>
    </div>

    <!-- Window Content -->
    <div class="window-content" v-show="!isMinimized">
      <slot></slot>
    </div>

    <!-- Resize handles -->
    <div v-show="!isMinimized" class="resize-handles">
      <!-- Corner handles -->
      <div class="resize-handle corner top-left" @mousedown="startResize('nw', $event)"></div>
      <div class="resize-handle corner top-right" @mousedown="startResize('ne', $event)"></div>
      <div class="resize-handle corner bottom-left" @mousedown="startResize('sw', $event)"></div>
      <div class="resize-handle corner bottom-right" @mousedown="startResize('se', $event)"></div>
      
      <!-- Edge handles -->
      <div class="resize-handle edge top" @mousedown="startResize('n', $event)"></div>
      <div class="resize-handle edge bottom" @mousedown="startResize('s', $event)"></div>
      <div class="resize-handle edge left" @mousedown="startResize('w', $event)"></div>
      <div class="resize-handle edge right" @mousedown="startResize('e', $event)"></div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from 'vue'

export default {
  name: 'ResizableWindow',
  props: {
    title: {
      type: String,
      default: 'Window'
    },
    initialWidth: {
      type: Number,
      default: 800
    },
    initialHeight: {
      type: Number,
      default: 600
    },
    initialX: {
      type: Number,
      default: 50
    },
    initialY: {
      type: Number,
      default: 50
    },
    minWidth: {
      type: Number,
      default: 300
    },
    minHeight: {
      type: Number,
      default: 200
    }
  },
  setup(props) {
    const windowElement = ref(null)
    const width = ref(props.initialWidth)
    const height = ref(props.initialHeight)
    const x = ref(props.initialX)
    const y = ref(props.initialY)
    const isMinimized = ref(false)
    
    const isDragging = ref(false)
    const isResizing = ref(false)
    const resizeDirection = ref('')
    const startMouseX = ref(0)
    const startMouseY = ref(0)
    const startX = ref(0)
    const startY = ref(0)
    const startWidth = ref(0)
    const startHeight = ref(0)

    const windowStyle = computed(() => ({
      width: `${width.value}px`,
      height: isMinimized.value ? '40px' : `${height.value}px`,
      left: `${x.value}px`,
      top: `${y.value}px`,
      zIndex: isDragging.value || isResizing.value ? 1000 : 1
    }))

    const startDrag = (e) => {
      if (e.target.classList.contains('control-btn')) return
      
      isDragging.value = true
      startMouseX.value = e.clientX
      startMouseY.value = e.clientY
      startX.value = x.value
      startY.value = y.value
      
      document.addEventListener('mousemove', drag)
      document.addEventListener('mouseup', stopDrag)
      e.preventDefault()
    }

    const drag = (e) => {
      if (!isDragging.value) return
      
      const deltaX = e.clientX - startMouseX.value
      const deltaY = e.clientY - startMouseY.value
      
      x.value = Math.max(0, startX.value + deltaX)
      y.value = Math.max(0, startY.value + deltaY)
    }

    const stopDrag = () => {
      isDragging.value = false
      document.removeEventListener('mousemove', drag)
      document.removeEventListener('mouseup', stopDrag)
    }

    const startResize = (direction, e) => {
      isResizing.value = true
      resizeDirection.value = direction
      startMouseX.value = e.clientX
      startMouseY.value = e.clientY
      startWidth.value = width.value
      startHeight.value = height.value
      startX.value = x.value
      startY.value = y.value
      
      document.addEventListener('mousemove', resize)
      document.addEventListener('mouseup', stopResize)
      e.preventDefault()
      e.stopPropagation()
    }

    const resize = (e) => {
      if (!isResizing.value) return
      
      const deltaX = e.clientX - startMouseX.value
      const deltaY = e.clientY - startMouseY.value
      const direction = resizeDirection.value
      
      let newWidth = startWidth.value
      let newHeight = startHeight.value
      let newX = startX.value
      let newY = startY.value

      // Handle horizontal resizing
      if (direction.includes('e')) {
        newWidth = Math.max(props.minWidth, startWidth.value + deltaX)
      }
      if (direction.includes('w')) {
        newWidth = Math.max(props.minWidth, startWidth.value - deltaX)
        if (newWidth > props.minWidth) {
          newX = startX.value + deltaX
        }
      }

      // Handle vertical resizing
      if (direction.includes('s')) {
        newHeight = Math.max(props.minHeight, startHeight.value + deltaY)
      }
      if (direction.includes('n')) {
        newHeight = Math.max(props.minHeight, startHeight.value - deltaY)
        if (newHeight > props.minHeight) {
          newY = startY.value + deltaY
        }
      }

      width.value = newWidth
      height.value = newHeight
      x.value = newX
      y.value = newY
    }

    const stopResize = () => {
      isResizing.value = false
      resizeDirection.value = ''
      document.removeEventListener('mousemove', resize)
      document.removeEventListener('mouseup', stopResize)
    }

    const toggleMinimize = () => {
      isMinimized.value = !isMinimized.value
    }

    onUnmounted(() => {
      document.removeEventListener('mousemove', drag)
      document.removeEventListener('mouseup', stopDrag)
      document.removeEventListener('mousemove', resize)
      document.removeEventListener('mouseup', stopResize)
    })

    return {
      windowElement,
      windowStyle,
      isMinimized,
      startDrag,
      startResize,
      toggleMinimize
    }
  }
}
</script>

<style scoped>
.resizable-window {
  position: absolute;
  background: #2c2c2c;
  border: 1px solid #444;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  overflow: hidden;
  user-select: none;
}

.window-header {
  background: linear-gradient(135deg, #3c3c3c, #2c2c2c);
  border-bottom: 1px solid #444;
  padding: 0.5rem 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: move;
  height: 40px;
  box-sizing: border-box;
}

.window-title {
  color: #e0b566;
  font-weight: bold;
  font-size: 0.9rem;
  text-overflow: ellipsis;
  overflow: hidden;
  white-space: nowrap;
}

.window-controls {
  display: flex;
  gap: 0.25rem;
}

.control-btn {
  width: 20px;
  height: 20px;
  border: none;
  border-radius: 3px;
  background: #444;
  color: #fff;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  transition: background-color 0.2s;
}

.control-btn:hover {
  background: #555;
}

.minimize-btn:hover {
  background: #666;
}

.window-content {
  padding: 0;
  height: calc(100% - 40px);
  overflow: auto;
}

.resize-handles {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
}

.resize-handle {
  position: absolute;
  pointer-events: all;
}

/* Corner handles */
.resize-handle.corner {
  width: 10px;
  height: 10px;
}

.resize-handle.top-left {
  top: -5px;
  left: -5px;
  cursor: nw-resize;
}

.resize-handle.top-right {
  top: -5px;
  right: -5px;
  cursor: ne-resize;
}

.resize-handle.bottom-left {
  bottom: -5px;
  left: -5px;
  cursor: sw-resize;
}

.resize-handle.bottom-right {
  bottom: -5px;
  right: -5px;
  cursor: se-resize;
}

/* Edge handles */
.resize-handle.edge.top {
  top: -3px;
  left: 10px;
  right: 10px;
  height: 6px;
  cursor: n-resize;
}

.resize-handle.edge.bottom {
  bottom: -3px;
  left: 10px;
  right: 10px;
  height: 6px;
  cursor: s-resize;
}

.resize-handle.edge.left {
  left: -3px;
  top: 10px;
  bottom: 10px;
  width: 6px;
  cursor: w-resize;
}

.resize-handle.edge.right {
  right: -3px;
  top: 10px;
  bottom: 10px;
  width: 6px;
  cursor: e-resize;
}

/* Visual feedback for resize handles */
.resize-handle.corner {
  background: rgba(224, 181, 102, 0.3);
  border: 1px solid rgba(224, 181, 102, 0.6);
  border-radius: 50%;
}

.resize-handle.corner:hover {
  background: rgba(224, 181, 102, 0.5);
}
</style>