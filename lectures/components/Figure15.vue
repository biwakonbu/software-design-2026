<script setup>
import "../styles/learning-course.css"
import diagrams from "../data/figures15.json"
defineProps({index:Number})
</script>
<template><CourseDiagram :diagram="diagrams[index]" :uid="`lesson15-${index}`" /></template>
