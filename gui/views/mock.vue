<script setup>

</script>

<template lang="pug">
.content    
    h2 Mock
    p Simulated agents
hr

.content
    p 
        | Mock adds a set of simulated agents to CALDERA and allows you to run complete operations without hooking any
        | other computers up to your server. All simulated agents will appear as normal agents in the UI and can be
        | used in any operation.

.is-flex.is-align-items-center.is-justify-content-center
    a.button.is-primary(href="/docs/Plugin-library.html#mock" target="_blank")
        span Read more here
        span.icon
            font-awesome-icon(icon="fas fa-angle-right")

</template>