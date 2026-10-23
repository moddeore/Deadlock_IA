# Deadlock Lab — OS Activity 2

An original educational dashboard for deadlock analysis and resource allocation, built with Python and Streamlit.

## Features
- Banker's Algorithm: Need matrix, safe sequence, Work-vector trace
- Resource-request validation: Need, Available, and post-allocation safety checks
- Separate multi-instance deadlock detection simulation
- Prevention policy and conceptual recovery demonstration
- Six required assignment test cases and boundary-input checklist
- Editable AI usage record

## Run on Windows
1. Install Python 3.10 or newer from https://www.python.org/downloads/ and enable **Add Python to PATH**.
2. Extract the project folder.
3. Open Command Prompt in the folder containing `app.py`.
4. Run:
   ```bash
   python -m pip install -r requirements.txt
   python -m streamlit run app.py
   ```
5. Open the local URL shown in the terminal (usually http://localhost:8501).

## Notes
- This is a simulation; it does not manage real OS processes or resource locks.
- The test-case table contains expected outcomes. Run each scenario and record actual results before submitting.
- Edit the AI usage record to match the tools your group actually used.
- The default Banker example is the standard five-process, three-resource example.
