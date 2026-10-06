<script setup>
import "../styles/learning-course.css"
import diagrams from "../data/figures14.json"
defineProps({index:Number})
</script>
<template><CourseDiagram :diagram="diagrams[index]" :uid="`lesson14-${index}`" /></template>
