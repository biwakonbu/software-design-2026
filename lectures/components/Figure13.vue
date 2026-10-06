<script setup>
import "../styles/learning-course.css"
import diagrams from "../data/figures13.json"
defineProps({index:Number})
</script>
<template><CourseDiagram :diagram="diagrams[index]" :uid="`lesson13-${index}`" /></template>
