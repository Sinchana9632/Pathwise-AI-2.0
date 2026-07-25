# Chapter 1: Project Overview

## 1.1 Project Title
PathWise AI (Version 2.0)

## 1.2 Abstract
PathWise AI 2.0 is a smart career assistant built to help final-year engineering students prepare for campus placements. Unlike regular tools that only scan a resume once and forget it, our system uses a smart Large Language Model (Llama 3.1) alongside a local SQLite database memory. This allows the system to save a user's account details, identify their technical skill gaps, and use an interactive AI mentor chatbot to guide them day-by-day until their skills and resume are fully ready for production.

## 1.3 Problem Statement
Most current resume checking platforms suffer from two major problems:
1. They rely on simple keyword counting (like a `Ctrl+F` scan). If a job description asks for a skill and the student writes a valid project synonym instead of the exact word, the system flags it as a failure.
2. They operate with complete "amnesia." Every time a user closes the browser or logs out, all their evaluation scores and historical progress are permanently wiped out, forcing them to start over from scratch.

## 1.4 Objectives
* To build a secure system where students can create an account and safely store their profile progress.
* To implement a contextual AI analyzer that evaluates resumes like a real human manager instead of just matching flat keywords.
* To create an interactive, stateful AI Career Mentor chatbot that remembers a student's technical gaps and tracks their updates over time.

## 1.5 Scope of Project
This project is designed as a desktop-based SaaS web application tailored specifically for student placement preparation cycles. The application handles secure login, PDF text parsing, AI skill gap analysis, interactive chat tracking, and automatic generation of clean, ATS-compliant PDF resumes.