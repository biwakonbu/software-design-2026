<script setup>
import "../styles/learning-course.css"
import diagrams from "../data/figures09.json"
defineProps({index:Number})
</script>
<template><CourseDiagram :diagram="diagrams[index]" :uid="`lesson09-${index}`" /></template>
