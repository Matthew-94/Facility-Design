# Facility-Design
Course Codes
# LayoutWise: CRAFT & CORELAP Facility Layout Planner

A Python-based graphical application for solving **facility layout planning problems** using two classic layout algorithms:

- **CORELAP** (Computerized Relationship Layout Planning)
- **CRAFT** (Computerized Relative Allocation of Facilities Technique)

This project provides an interactive desktop GUI built with **Tkinter**, allowing users to define layout problems, enter relationship/flow data, generate initial layouts, and visualize optimization results.

---

## Overview

Facility layout design is an important problem in industrial engineering and operations management. The goal is to arrange departments, workstations, or facilities in a way that improves adjacency relationships and reduces movement cost.

This application combines two well-known approaches:

### 1. CORELAP
CORELAP is a **constructive layout algorithm**. It builds a layout step by step based on closeness relationships between departments.

In this application, the CORELAP module allows the user to:

- define the number of departments
- enter REL chart values (`A, E, I, O, U, X`)
- customize closeness weights
- set the partial adjacency factor
- generate the numerical closeness value matrix
- calculate TCR values
- display placement sequence and step-by-step selection logic
- visualize the final block layout
- generate the rectilinear distance matrix
- compute the final layout score

### 2. CRAFT
CRAFT is an **improvement-based layout algorithm**. It starts from an initial layout and iteratively improves it by swapping departments to reduce total material handling cost.

In this application, the CRAFT module allows the user to:

- define facility dimensions and scale
- define departments as fixed or variable
- enter department areas
- create an initial layout manually or automatically
- define flow and cost matrices
- define fixed points and fixed-point costs
- choose distance metric:
  - Rectilinear
  - Euclidean
- choose initial solution mode:
  - Sequential
  - Random
  - Leave Blank
- choose solution mode:
  - Traditional Craft
  - Opt. Sequence
- visualize both initial and optimized layouts
- track centroid coordinates, inflow, and outflow
- display iteration logs for each accepted or rejected swap
- optionally display flow lines on the layout

---

## Features

- Interactive **Tkinter GUI**
- Separate modules for **CORELAP** and **CRAFT**
- Main menu for launching each algorithm
- Manual and random problem generation
- Excel-style pasting for REL chart input in CORELAP
- Flow/cost matrix input for CRAFT
- Fixed-point support in CRAFT
- Step-by-step execution log
- Layout visualization on canvas
- Initial and final layout comparison
- Department centroid and flow statistics
- Educational and practical use for facility layout courses

---

## Project Structure

```bash
.
├── layoutwise_app.py      # Main Python application
└── README.md
