<script setup>
import "../styles/learning-course.css"
import diagrams from "../data/figures12.json"
defineProps({index:Number})
</script>
<template><CourseDiagram :diagram="diagrams[index]" :uid="`lesson12-${index}`" /></template>
