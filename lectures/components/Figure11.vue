<script setup>
import "../styles/learning-course.css"
import diagrams from "../data/figures11.json"
defineProps({index:Number})
</script>
<template><CourseDiagram :diagram="diagrams[index]" :uid="`lesson11-${index}`" /></template>
