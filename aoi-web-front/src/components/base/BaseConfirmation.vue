<template>
    <!-- <teleport to="body"> -->
    <div class = "modal-mask">
        <div class = "modal-wrapper">
        <div class = "modal-body">
            <p>{{confirmText}}</p>
            <button class ="modal-button" @click="acceptModal" >Accept</button>
            <button class ="modal-button" @click="declineModal">Decline</button>
        </div>
        </div>
    </div>
    <!-- </teleport> -->
</template>

<script>
export default {
  props: ['confirmText'],

  emits: ['accept','decline'],
                  
  setup(props, context){

    function acceptModal()
    {
        context.emit('accept')
    }

    function declineModal()
    {
        context.emit('decline')
    }

    return{
        acceptModal,
        declineModal
    }


  }
}
</script>

<style scoped>
.modal-mask{
    position: fixed;
    z-index:9998;
    top:0;
    left:0;
    width: 100%;
    height: 100%;
    background-color:rgba(0,0,0,0.4);
    display: table;
    transition: opacity 1s ease;;
}

.modal-wrapper{
    display: table-cell;
    vertical-align: middle;
}
.modal-body{
    width: 300px;
    margin: 0px auto;
    border-radius: 4px;
    padding: 20px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.33);
    background-color: gray;
    transition: all 1s ease;
}

.modal-button{
    margin-left: 10px;
    margin-right: 10px;
}
accept-button{
}
</style>