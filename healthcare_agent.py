"""
Healthcare Agent - Agentic AI System (Robust Version)
======================================================
This module implements an autonomous healthcare AI agent that can:
- Plan multi-step workflows
- Use tools to perform actions
- Reason about patient needs
- Maintain context across sessions
- Work with or without Ollama
"""

import json
import re
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum


class AgentState(Enum):
    """Agent execution states"""
    IDLE = "idle"
    THINKING = "thinking"
    ACTING = "acting"
    WAITING = "waiting"
    COMPLETED = "completed"
    ERROR = "error"


@dataclass
class Tool:
    """Tool definition for the agent"""
    name: str
    description: str
    parameters: Dict[str, str]
    function: callable


@dataclass
class AgentThought:
    """Represents an agent thought/action"""
    thought: str
    action: str
    action_input: Dict[str, Any]
    observation: str = ""


@dataclass
class PatientContext:
    """Patient session context"""
    patient_id: str = ""
    name: str = ""
    symptoms: List[str] = field(default_factory=list)
    medical_history: List[str] = field(default_factory=list)
    current_reports: List[str] = field(default_factory=list)
    recommended_doctors: List[Dict] = field(default_factory=list)
    pending_actions: List[str] = field(default_factory=list)
    completed_actions: List[str] = field(default_factory=list)


class HealthcareAgent:
    """
    Autonomous Healthcare Agent that can:
    - Analyze medical reports
    - Recommend doctors
    - Schedule appointments
    - Provide health advice
    - Remember patient context
    """
    
    def __init__(self, model: str = "llama3.2"):
        self.model = model
        self.state = AgentState.IDLE
        self.thoughts: List[AgentThought] = []
        self.context = PatientContext()
        self.tools: Dict[str, Tool] = {}
        self.max_iterations = 5
        self.ollama_available = self._check_ollama()
        
    def _check_ollama(self) -> bool:
        """Check if Ollama is available"""
        try:
            import ollama
            ollama.list()
            return True
        except:
            return False
    
    def register_tool(self, tool: Tool):
        """Register a tool for the agent to use"""
        self.tools[tool.name] = tool
    
    def register_tools_dict(self, tools_dict: Dict[str, callable]):
        """Register tools from a dictionary of functions"""
        for name, func in tools_dict.items():
            tool = Tool(
                name=name,
                description=func.__doc__ or f"Tool to {name.replace('_', ' ')}",
                parameters={},
                function=func
            )
            self.tools[name] = tool
    
    def set_context(self, patient_id: str = "", name: str = "", symptoms: List[str] = None):
        """Set patient context"""
        self.context.patient_id = patient_id or self.context.patient_id
        self.context.name = name or self.context.name
        if symptoms:
            self.context.symptoms = symptoms
    
    def think(self, user_request: str) -> str:
        """Agent reasoning step - decides what action to take next"""
        if self.ollama_available:
            try:
                return self._think_with_ollama(user_request)
            except Exception as e:
                print(f"Ollama error: {e}, falling back to rule-based")
        
        return self._think_rule_based(user_request)
    
    def _think_with_ollama(self, user_request: str) -> str:
        """Use Ollama for reasoning"""
        import ollama
        context_prompt = self._build_context_prompt(user_request)
        
        response = ollama.chat(
            model=self.model,
            messages=[
                {'role': 'system', 'content': self._get_system_prompt()},
                {'role': 'user', 'content': context_prompt}
            ]
        )
        return response['message']['content']
    
    def _think_rule_based(self, user_request: str) -> str:
        """Rule-based reasoning when Ollama is not available"""
        request_lower = user_request.lower()
        
        # Check for symptom-related requests
        symptom_keywords = ['symptom', 'feeling', 'hurt', 'pain', 'ache', 'fever', 'cough', 
                          'headache', 'sick', 'nausea', 'tired', 'fatigue', 'dizzy']
        if any(keyword in request_lower for keyword in symptom_keywords):
            action = "check_symptoms"
            symptoms = self._extract_symptoms(user_request)
            action_input = {"symptoms": symptoms}
        
        # Check for doctor-related requests
        elif any(word in request_lower for word in ['doctor', 'specialist', 'cardiologist', 
                                                      'neurologist', 'find', 'appointment']):
            action = "find_doctors"
            specialty = self._extract_specialty(user_request)
            condition = self._extract_condition(user_request)
            action_input = {"specialty": specialty, "condition": condition}
        
        # Check for report analysis requests
        elif any(word in request_lower for word in ['report', 'analyze', 'analysis', 'pdf', 
                                                      'medical', 'test result']):
            action = "analyze_report"
            action_input = {"report_text": user_request}
        
        # Check for advice requests
        elif any(word in request_lower for word in ['advice', 'recommend', 'suggestion', 
                                                      'help', 'what should']):
            action = "provide_advice"
            condition = self._extract_condition(user_request)
            action_input = {"condition": condition}
        
        # Check for appointment scheduling
        elif any(word in request_lower for word in ['schedule', 'book', 'appointment', 
                                                      'visit', 'meeting']):
            action = "schedule_appointment"
            doctor_name = self._extract_doctor(user_request)
            specialty = self._extract_specialty(user_request)
            action_input = {
                "doctor_name": doctor_name or "Any Available Doctor",
                "specialty": specialty or "General Physician",
                "patient_name": self.context.name or "Guest"
            }
        
        # Default: provide general advice
        else:
            action = "provide_advice"
            action_input = {"condition": "general health concern"}
        
        input_json = json.dumps(action_input)
        return f"""THINK: The user is asking about "{user_request}". Based on the request, I should use the {action} tool to help them.

ACTION: {action}
INPUT: {input_json}"""
    
    def _extract_symptoms(self, text: str) -> List[str]:
        """Extract symptoms from user text"""
        common_symptoms = ['fever', 'cough', 'headache', 'fatigue', 'nausea', 'dizziness',
                          'chest pain', 'stomach pain', 'back pain', 'joint pain', 'sore throat',
                          'runny nose', 'shortness of breath', 'loss of appetite', 'insomnia',
                          'anxiety', 'depression', 'rash', 'swelling']
        
        text_lower = text.lower()
        found_symptoms = [s for s in common_symptoms if s in text_lower]
        
        if not found_symptoms:
            words = text_lower.replace('?', '').replace('!', '').split()
            found_symptoms = [w for w in words if len(w) > 3][:5]
        
        return found_symptoms if found_symptoms else ['general discomfort']
    
    def _extract_specialty(self, text: str) -> str:
        """Extract doctor specialty from text"""
        # Map lowercase keys to proper specialty names
        specialties = {
            'heart': 'Cardiologist', 'cardiac': 'Cardiologist', 'chest pain': 'Cardiologist',
            'brain': 'Neurologist', 'neurological': 'Neurologist', 'headache': 'Neurologist',
            'seizure': 'Neurologist', 'diabetes': 'Endocrinologist', 'hormone': 'Endocrinologist',
            'bone': 'Orthopedic', 'joint': 'Orthopedic', 'fracture': 'Orthopedic',
            'skin': 'Dermatologist', 'rash': 'Dermatologist', 'lung': 'Pulmonologist',
            'breathing': 'Pulmonologist', 'kidney': 'Nephrologist', 'liver': 'Gastroenterologist',
            'stomach': 'Gastroenterologist', 'eye': 'Ophthalmologist', 'cancer': 'Oncologist',
            'mental': 'Psychiatrist', 'depression': 'Psychiatrist', 'anxiety': 'Psychiatrist',
            'cardio': 'Cardiologist', 'cardiologist': 'Cardiologist', 'cardio-': 'Cardiologist',
            'cardiology': 'Cardiologist',
            'neuro': 'Neurologist', 'neurologist': 'Neurologist', 'neurology': 'Neurologist',
            'ortho': 'Orthopedic', 'orthopedic': 'Orthopedic', 'orthopedics': 'Orthopedic',
            'derma': 'Dermatologist', 'dermatologist': 'Dermatologist', 'dermatology': 'Dermatologist',
            'pulmo': 'Pulmonologist', 'pulmonologist': 'Pulmonologist', 'pulmonology': 'Pulmonologist',
            'nephro': 'Nephrologist', 'nephrologist': 'Nephrologist', 'nephrology': 'Nephrologist',
            'gastro': 'Gastroenterologist', 'gastroenterologist': 'Gastroenterologist', 'gastroenterology': 'Gastroenterologist',
            'ophthal': 'Ophthalmologist', 'ophthalmologist': 'Ophthalmologist', 'ophthalmology': 'Ophthalmologist',
            'onco': 'Oncologist', 'oncologist': 'Oncologist', 'oncology': 'Oncologist',
            'psychi': 'Psychiatrist', 'psychiatrist': 'Psychiatrist', 'psychiatry': 'Psychiatrist',
            'endo': 'Endocrinologist', 'endocrinologist': 'Endocrinologist', 'endocrinology': 'Endocrinologist'
        }
        
        text_lower = text.lower()
        for key, spec in specialties.items():
            if key in text_lower:
                return spec
        return "General Physician"
    
    def _extract_condition(self, text: str) -> str:
        """Extract medical condition from text"""
        # Don't extract specialty-related terms as conditions
        # These should be handled by _extract_specialty
        specialty_terms = ['cardiologist', 'cardiologist', 'cardio', 'cardiology',
                         'neurologist', 'neurology', 'neuro',
                         'dermatologist', 'dermatology', 'derma',
                         'orthopedic', 'orthopedics', 'ortho',
                         'pulmonologist', 'pulmonology', 'pulmo',
                         'nephrologist', 'nephrology', 'nephro',
                         'gastroenterologist', 'gastroenterology', 'gastro',
                         'ophthalmologist', 'ophthalmology', 'ophthal',
                         'oncologist', 'oncology', 'onco',
                         'psychiatrist', 'psychiatry', 'psychi',
                         'endocrinologist', 'endocrinology', 'endo']
        
        text_lower = text.lower()
        
        # First check if this is a specialty request - if so, don't extract condition
        if any(term in text_lower for term in specialty_terms):
            return "general health concern"
        
        # Only extract specific medical conditions
        conditions = ['diabetes', 'heart disease', 'cancer', 'asthma', 'hypertension',
                     'arthritis', 'depression', 'anxiety', 'flu', 'cold', 'infection',
                     'migraine', 'allergies', 'pneumonia', 'bronchitis', 'gastritis',
                     'thyroid', 'anemia', 'obesity', 'insomnia', 'acid reflux']
        
        for condition in conditions:
            if condition in text_lower:
                return condition
        
        # Only extract generic terms if no specific condition found
        if 'pain' in text_lower:
            return "pain"
        if 'fever' in text_lower:
            return "fever"
        if 'cough' in text_lower:
            return "cough"
            
        return "general health concern"
    
    def _extract_doctor(self, text: str) -> str:
        """Extract doctor name from text"""
        patterns = [r'dr\.?\s+(\w+)', r'doctor\s+(\w+)']
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return f"Dr. {match.group(1)}"
        return ""
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt that defines agent behavior"""
        tools_list = "\n".join([f"- {name}: {tool.description}" for name, tool in self.tools.items()])
        
        return f"""You are an intelligent Healthcare AI Agent. Your role is to help patients by:
1. ANALYZING medical reports and explaining findings
2. RECOMMENDING appropriate specialists based on symptoms/conditions
3. SCHEDULING appointments with doctors
4. PROVIDING health advice and lifestyle recommendations
5. TRACKING patient history and follow-ups

Available Tools:
{tools_list}

For each user request:
1. THINK about what needs to be done
2. DECIDE which tool to use
3. ACT by calling the appropriate tool

Always be empathetic, clear, and actionable. Prioritize patient safety.
Format your response as:
THINK: [your reasoning]
ACTION: [tool_name]
INPUT: {{"key": "value"}}"""
    
    def _build_context_prompt(self, user_request: str) -> str:
        """Build context prompt with patient history and available tools"""
        tools_description = "\n".join([f"- {name}: {tool.description}" for name, tool in self.tools.items()])
        
        return f"""
Current Patient Context:
- Patient ID: {self.context.patient_id}
- Name: {self.context.name}
- Symptoms: {', '.join(self.context.symptoms)}
- Medical History: {', '.join(self.context.medical_history)}
- Completed Actions: {', '.join(self.context.completed_actions)}

Available Tools:
{tools_description}

User Request: {user_request}

Based on the context and available tools, decide what action to take next.
"""
    
    def execute_plan(self, user_request: str) -> Dict[str, Any]:
        """Execute a multi-step plan to fulfill user request"""
        self.state = AgentState.THINKING
        self.thoughts = []
        
        result = {'success': False, 'message': '', 'actions_taken': [], 'final_result': None}
        
        # If no tools registered, try to register default tools
        if not self.tools:
            self._register_default_tools()
        
        for iteration in range(self.max_iterations):
            thought_response = self.think(user_request)
            thought, action, action_input = self._parse_thought(thought_response)
            
            if not action:
                result['success'] = True
                result['final_result'] = thought or "I'm here to help! You can ask me to analyze symptoms, find doctors, or provide health advice."
                break
            
            agent_thought = AgentThought(thought=thought, action=action, action_input=action_input)
            self.thoughts.append(agent_thought)
            
            self.state = AgentState.ACTING
            try:
                if action in self.tools:
                    observation = self.tools[action].function(**action_input)
                    agent_thought.observation = str(observation)
                    result['actions_taken'].append({'action': action, 'input': action_input, 'observation': observation})
                    self._update_context(action, action_input, observation)
                else:
                    agent_thought.observation = f"Unknown action: {action}. Available: {list(self.tools.keys())}"
            except Exception as e:
                agent_thought.observation = f"Error: {str(e)}"
                result['message'] = str(e)
            
            if self._is_complete(action, agent_thought.observation):
                result['success'] = True
                result['final_result'] = self._format_result(agent_thought.observation)
                break
            
            if action and agent_thought.observation:
                result['success'] = True
                result['final_result'] = self._format_result(agent_thought.observation)
                break
        
        self.state = AgentState.COMPLETED
        return result
    
    def _register_default_tools(self):
        """Register default tools if none provided"""
        try:
            from agent_tools import AGENT_TOOLS
            self.register_tools_dict(AGENT_TOOLS)
        except Exception as e:
            print(f"Could not load default tools: {e}")
    
    def _parse_thought(self, response: str) -> tuple:
        """Parse agent response to extract thought, action, and input"""
        thought = ""
        action = ""
        action_input = {}
        
        lines = response.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('THINK:'):
                thought = line[6:].strip()
            elif line.startswith('ACTION:'):
                action = line[7:].strip()
            elif line.startswith('INPUT:'):
                try:
                    input_str = line[6:].strip()
                    if input_str.startswith('{'):
                        action_input = json.loads(input_str)
                except:
                    try:
                        json_match = re.search(r'\{[^}]+\}', response)
                        if json_match:
                            action_input = json.loads(json_match.group())
                    except:
                        pass
        
        return thought, action, action_input
    
    def _update_context(self, action: str, action_input: Dict, observation: Any):
        """Update patient context based on action results"""
        self.context.completed_actions.append(action)
        
        if action == "find_doctors" and observation:
            try:
                if isinstance(observation, dict) and 'doctors' in observation:
                    self.context.recommended_doctors = observation['doctors']
            except:
                pass
        
        if action == "check_symptoms" and observation:
            try:
                if isinstance(observation, dict) and 'possible_condition' in observation:
                    self.context.medical_history.append(observation['possible_condition'])
            except:
                pass
    
    def _is_complete(self, action: str, observation: str) -> bool:
        """Check if the task is complete"""
        if action and observation and "error" not in observation.lower():
            final_actions = ["provide_advice", "schedule_appointment", "check_symptoms", "find_doctors", "analyze_report"]
            return action in final_actions
        return False
    
    def _format_result(self, observation: str) -> str:
        """Format the final result for display"""
        try:
            if observation.startswith('{'):
                data = json.loads(observation)
                return self._format_json_result(data)
        except:
            pass
        return observation
    
    def _format_json_result(self, data: Dict) -> str:
        """Format JSON observation into readable text"""
        if isinstance(data, dict):
            parts = []
            if 'success' in data and data['success']:
                parts.append("✓ Action completed successfully")
            
            if 'analysis' in data:
                parts.append(f"\n📊 Analysis:\n{data['analysis']}")
            
            if 'doctors' in data:
                doctors = data['doctors']
                if isinstance(doctors, list) and doctors:
                    parts.append(f"\n👨‍⚕️ Recommended Doctors:")
                    for doc in doctors[:3]:
                        if isinstance(doc, dict):
                            parts.append(f"   - {doc.get('name', 'Doctor')}: {doc.get('experience', '')} experience, Rating: {doc.get('rating', 'N/A')}")
            
            if 'advice' in data:
                parts.append(f"\n💡 Health Advice:\n{data['advice']}")
            
            if 'possible_condition' in data:
                parts.append(f"\n🔍 Possible Condition: {data['possible_condition']}")
                if 'confidence' in data:
                    parts.append(f"   Confidence: {int(data['confidence'] * 100)}%")
                if 'recommendation' in data:
                    parts.append(f"   Recommendation: {data['recommendation']}")
            
            if 'appointment' in data:
                appt = data['appointment']
                if isinstance(appt, dict):
                    parts.append(f"\n📅 Appointment Scheduled:")
                    parts.append(f"   Doctor: {appt.get('doctor_name', 'N/A')}")
                    parts.append(f"   Date: {appt.get('date', 'N/A')}")
                    parts.append(f"   Time: {appt.get('time', 'N/A')}")
            
            if 'message' in data:
                parts.append(f"\n{data['message']}")
            
            return '\n'.join(parts) if parts else str(data)
        return str(data)
    
    def get_status(self) -> Dict[str, Any]:
        """Get current agent status"""
        return {
            'state': self.state.value,
            'ollama_available': self.ollama_available,
            'registered_tools': list(self.tools.keys()),
            'context': {
                'patient_id': self.context.patient_id,
                'name': self.context.name,
                'symptoms': self.context.symptoms,
                'completed_actions': self.context.completed_actions
            },
            'thoughts': [{'thought': t.thought, 'action': t.action, 'observation': t.observation} for t in self.thoughts]
        }


# Default agent instance
default_agent = HealthcareAgent()


def create_agent(model: str = "llama3.2") -> HealthcareAgent:
    """Factory function to create a new agent instance"""
    return HealthcareAgent(model)


def register_tools(agent: HealthcareAgent, tool_functions: Dict[str, callable]):
    """Register external tool functions with the agent"""
    for name, func in tool_functions.items():
        tool = Tool(
            name=name,
            description=func.__doc__ or f"Tool to {name.replace('_', ' ')}",
            parameters={},
            function=func
        )
        agent.register_tool(tool)