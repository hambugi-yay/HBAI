# HB AI - Korean-English Conversational AI

## Overview

HB AI is a Streamlit-based conversational AI application that provides bilingual support for Korean and English languages. The application utilizes the Qwen2-7B-Instruct model for text generation and features a user-friendly web interface for real-time chat interactions. The system is designed with a mock fallback mechanism to ensure functionality even when model dependencies are unavailable, making it robust for development and testing environments.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Framework**: Streamlit web application framework for rapid UI development
- **Language Support**: Bilingual interface supporting Korean and English with dynamic language switching
- **UI Components**: Modular component system with dedicated `UIComponents` class for rendering sidebar, model status, and chat controls
- **Session Management**: Streamlit's session state for maintaining chat history and application state

### Backend Architecture
- **Model Management**: Dedicated `ModelManager` class for handling AI model loading, inference, and resource management
- **Mock System**: `MockModelManager` fallback system that simulates model behavior for testing and development when dependencies are unavailable
- **Text Processing**: Specialized `KoreanTextProcessor` for handling Korean text formatting, prompt preparation, and response post-processing
- **Memory Management**: Automatic garbage collection and CUDA memory cleanup for optimal resource usage

### AI Model Integration
- **Primary Model**: Qwen2-7B-Instruct for conversational AI capabilities
- **Quantization**: 4-bit quantization using BitsAndBytesConfig for improved performance and reduced memory usage
- **Device Management**: Automatic CUDA/CPU device detection and configuration
- **Context Handling**: Conversation history management with proper chat formatting and context window management

### Text Processing Pipeline
- **Korean Language Support**: Pattern recognition for Korean characters and mixed-language text
- **Prompt Engineering**: Specialized prompt formatting for Korean and English inputs
- **Response Processing**: Post-processing pipeline for improving Korean text quality and formatting
- **Chat Context**: Conversation history formatting with proper role-based message structure

## External Dependencies

### Core AI Libraries
- **transformers**: Hugging Face transformers library for model loading and tokenization
- **torch**: PyTorch for deep learning model execution and CUDA support
- **BitsAndBytesConfig**: Quantization library for memory-efficient model loading

### Web Framework
- **streamlit**: Primary web application framework for UI rendering and session management

### System Libraries
- **os**: Environment variable access and system configuration
- **gc**: Garbage collection for memory management
- **re**: Regular expressions for Korean text pattern matching
- **time**: Timing utilities for progress simulation and response delays
- **random**: Random number generation for mock response selection
- **traceback**: Error handling and debugging support

### Model Source
- **Hugging Face Model Hub**: Qwen/Qwen2-7B-Instruct model repository for downloading the conversational AI model