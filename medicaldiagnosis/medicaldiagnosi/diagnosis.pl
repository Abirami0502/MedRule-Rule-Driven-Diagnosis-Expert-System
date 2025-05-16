% Test predicate to confirm file loading
test_consult_marker(loaded_successfully).

% --- Constants ---
bonus_per_risk_factor(5).
max_risk_factor_bonus(15).
answer_adjustment_factor(10). % Example adjustment value - Note: This constant is defined but not explicitly used in the provided symptom_match logic.

% ------------------------
% Disease Definitions
% disease(DiseaseName, [(SymptomAtom, Weight), ...]).
% ------------------------
disease(flu, [(fever, 0.8), (chills, 0.6), (headache, 0.5), (cough, 0.7), (sore_throat, 0.6), (body_ache, 0.7)]).
disease(common_cold, [(cough, 0.6), (sneezing, 0.8), (sore_throat, 0.5), (runny_nose, 0.9), (mild_fever, 0.4)]). % Assuming mild_fever is a distinct symptom atom
disease(covid19, [(fever, 0.9), (cough, 0.9), (shortness_of_breath, 1.0), (loss_of_taste, 0.8), (fatigue, 0.6)]).
disease(dengue, [(high_fever, 0.9), (rash, 0.6), (headache, 0.6), (joint_pain, 0.7), (nausea, 0.5), (bleeding, 0.8)]). % Assuming high_fever is distinct
disease(asthma, [(shortness_of_breath, 0.9), (wheezing, 0.8), (cough, 0.6), (chest_tightness, 0.7)]).
disease(migraine, [(headache, 0.9), (nausea, 0.5), (light_sensitivity, 0.7), (aura, 0.6)]).
disease(hypertension, [(headache, 0.4), (dizziness, 0.5), (blurred_vision, 0.6), (chest_pain, 0.7)]). % chest_pain may need differentiation if also in pneumonia
disease(diabetes, [(frequent_urination, 0.8), (increased_thirst, 0.8), (fatigue, 0.6), (blurred_vision, 0.5)]).
disease(pneumonia, [(cough, 0.8), (chest_pain, 0.7), (fever, 0.9), (difficulty_breathing, 0.9), (chills, 0.6)]).
disease(typhoid, [(prolonged_fever, 0.8), (weakness, 0.7), (abdominal_pain, 0.6), (constipation, 0.5), (headache, 0.5)]). % prolonged_fever distinct
disease(chickenpox, [(rash, 0.9), (fever, 0.6), (tiredness, 0.5), (loss_of_appetite, 0.4)]).
disease(tuberculosis, [(persistent_cough, 0.8), (weight_loss, 0.7), (night_sweats, 0.6), (fatigue, 0.6)]). % persistent_cough distinct
disease(bronchitis, [(cough, 0.9), (mucus, 0.7), (fatigue, 0.5), (shortness_of_breath, 0.6)]).
disease(hepatitis_b, [(jaundice, 0.9), (abdominal_pain, 0.6), (dark_urine, 0.8), (fatigue, 0.5)]).
disease(urinary_tract_infection, [(burning_urination, 0.9), (frequent_urination, 0.8), (pelvic_pain, 0.7)]).
disease(appendicitis, [(abdominal_pain, 0.9), (nausea, 0.6), (vomiting, 0.5), (fever, 0.7), (loss_of_appetite, 0.8)]).
disease(anemia, [(fatigue, 0.8), (pale_skin, 0.7), (dizziness, 0.6), (shortness_of_breath, 0.5), (cold_hands_feet, 0.4)]).
disease(sinusitis, [(facial_pain, 0.7), (nasal_congestion, 0.8), (headache, 0.6), (runny_nose, 0.7), (fever, 0.5)]).
disease(food_poisoning, [(nausea, 0.9), (vomiting, 0.9), (diarrhea, 0.8), (abdominal_cramps, 0.8), (fever, 0.6)]).
disease(allergic_rhinitis, [(sneezing, 0.9), (itchy_eyes, 0.8), (runny_nose, 0.8), (nasal_congestion, 0.6)]).
disease(constipation, [(infrequent_bowel, 0.9), (hard_stool, 0.8), (abdominal_pain, 0.6), (bloating, 0.5)]).

% ------------------------
% Risk Factors
% risk_factor(DiseaseName, [FactorAtom1, FactorAtom2, ...]).
% Note: Atoms with spaces need to be enclosed in single quotes.
% ------------------------
risk_factor(diabetes, [obesity, family_history, 'sedentary lifestyle', 'poor diet']).
risk_factor(hypertension, [stress, obesity, 'high salt intake', alcohol, smoking]).
risk_factor(covid19, ['crowded places', 'no mask', 'poor immunity']).
risk_factor(dengue, ['mosquito bites', 'stagnant water']).
risk_factor(tuberculosis, [malnutrition, 'hiv positive', overcrowding]).
risk_factor(hepatitis_b, ['unprotected sex', 'shared needles', 'blood transfusion']).
risk_factor(anemia, ['iron deficiency', 'chronic disease', 'blood loss']).
risk_factor(sinusitis, [allergies, 'cold weather']).
risk_factor(food_poisoning, ['contaminated food', 'poor hygiene']).
risk_factor(allergic_rhinitis, [dust, pollen, 'animal dander']).
risk_factor(constipation, ['low fiber diet', dehydration, inactivity]).

% ------------------------
% Test Recommendations
% requires_test(DiseaseName, TestAtomOrString).
% ------------------------
requires_test(covid19, pcr_test).
requires_test(dengue, blood_test).
requires_test(typhoid, widal_test).
requires_test(diabetes, hba1c_test).
requires_test(pneumonia, chest_xray).
requires_test(hypertension, blood_pressure_test).
requires_test(tuberculosis, sputum_test).
requires_test(hepatitis_b, hbsag_test).
requires_test(anemia, cbc_test).
requires_test(sinusitis, nasal_endoscopy).
requires_test(food_poisoning, stool_test).
requires_test(allergic_rhinitis, allergy_skin_test).
requires_test(constipation, physical_exam).
requires_test(appendicitis, 'ct_scan or ultrasound'). % String for test with space
requires_test(migraine, 'neurological exam').
requires_test(asthma, spirometry).
% Default: if no specific test, could add:
% requires_test(_, 'general consultation'). % Or handle this in Python if Prolog fails to find a test

% ------------------------
% Severity Classification
% ------------------------
severe(covid19). severe(dengue). severe(pneumonia). severe(hepatitis_b). severe(tuberculosis). severe(appendicitis).
moderate(typhoid). moderate(asthma). moderate(hypertension). moderate(urinary_tract_infection). moderate(food_poisoning). moderate(bronchitis).
mild(flu). mild(common_cold). mild(migraine). mild(chickenpox). mild(anemia). mild(sinusitis). mild(allergic_rhinitis). mild(constipation).

% ------------------------
% Symptom Scoring Logic
% symptom_score(UserReportedSymptomsList, DiseaseSymptomsListWithWeights, Score).
% ------------------------
symptom_score([], _, 0).
symptom_score([UserSymAtom | RestUserSymptoms], DiseaseSymptomList, TotalScore) :-
    ( member((UserSymAtom, Weight), DiseaseSymptomList) ->
        CurrentScore = Weight
    ;   CurrentScore = 0
    ),
    symptom_score(RestUserSymptoms, DiseaseSymptomList, RestScore),
    TotalScore is CurrentScore + RestScore.

% Total possible weight for a disease's defined symptoms
% total_weight(DiseaseSymptomsListWithWeights, TotalWeight).
total_weight([], 0).
total_weight([(_, W) | Rest], Total) :-
    total_weight(Rest, SubTotal),
    Total is SubTotal + W.

% ------------------------
% Risk Factor Bonus Logic
% risk_factor_bonus(UserRiskFactorList, DiseaseAtom, BonusScore).
% ------------------------
risk_factor_bonus(UserRiskFactors, Disease, BonusScore) :-
    risk_factor(Disease, DiseaseRiskFactors), % Check if risk factors are defined for the disease
    intersection(UserRiskFactors, DiseaseRiskFactors, MatchingFactors),
    length(MatchingFactors, NumMatching),
    bonus_per_risk_factor(BonusPer),
    max_risk_factor_bonus(MaxBonus),
    CalculatedBonus is NumMatching * BonusPer,
    BonusScore is min(CalculatedBonus, MaxBonus),
    !. % Cut: if risk_factor/2 succeeds, commit to this calculation
risk_factor_bonus(_, _, 0). % Default bonus if no risk_factor/2 match or no matching factors

% ------------------------
% Follow-up Questions
% follow_up_question(DiseaseAtom, QuestionString).
% ------------------------
follow_up_question(flu, 'Are the body aches severe?').
follow_up_question(flu, 'Did the symptoms appear suddenly?').
follow_up_question(common_cold, 'Is the fever generally low-grade or absent?').
follow_up_question(common_cold, 'Are symptoms mostly confined to the nose and throat?').
follow_up_question(covid19, 'Have you experienced a recent loss of smell or taste?').
follow_up_question(covid19, 'Have you been in close contact with a confirmed COVID-19 case?').
follow_up_question(dengue, 'Have you noticed any tiny red spots (petechiae) on your skin?').
follow_up_question(dengue, 'Have you recently traveled to an area where Dengue is common?').
follow_up_question(asthma, 'Does the shortness of breath worsen at night or with exercise?').
follow_up_question(asthma, 'Do you have a personal or family history of allergies or eczema?').
follow_up_question(migraine, 'Do you experience visual disturbances (aura) before the headache?').
follow_up_question(migraine, 'Is the headache usually on one side of the head?').
follow_up_question(hypertension, 'Do you have a history of high blood pressure readings?').
follow_up_question(hypertension, 'Are you currently taking medication for blood pressure?').
follow_up_question(diabetes, 'Have you noticed any unexplained weight loss?').
follow_up_question(diabetes, 'Do cuts or sores seem slow to heal?').
follow_up_question(pneumonia, 'Is the cough producing colored phlegm (yellow/green)?').
follow_up_question(pneumonia, 'Are you experiencing sharp chest pain, especially when breathing deeply?').
follow_up_question(typhoid, 'Have you consumed potentially contaminated food or water recently?').
follow_up_question(typhoid, 'Is the fever consistently high, especially in the evening?').
follow_up_question(chickenpox, 'Are the rash spots itchy and fluid-filled blisters?').
follow_up_question(chickenpox, 'Have you had chickenpox before or been vaccinated?').
follow_up_question(tuberculosis, 'Have you had unexplained weight loss recently?'). % This question is duplicated
follow_up_question(tuberculosis, 'Are you coughing up blood or blood-stained mucus?').
follow_up_question(bronchitis, 'Is the cough producing clear, white, or colored phlegm?'). % Similar to pneumonia's q
follow_up_question(bronchitis, 'How long has the cough persisted?').
follow_up_question(hepatitis_b, 'Have you ever been diagnosed with liver problems?').
follow_up_question(hepatitis_b, 'Is there yellowing of the skin or eyes (jaundice)?').
follow_up_question(urinary_tract_infection, 'Is there any blood visible in the urine?').
follow_up_question(urinary_tract_infection, 'Do you have pain in your back or side (flank pain)?').
follow_up_question(appendicitis, 'Is the abdominal pain primarily in the lower right side?').
follow_up_question(appendicitis, 'Does the pain worsen with movement or coughing?').
follow_up_question(anemia, 'Do you often feel weak or more tired than usual?').
follow_up_question(anemia, 'Does your diet include iron-rich foods (like red meat, spinach)?').
follow_up_question(sinusitis, 'Is there thick, colored nasal discharge?').
follow_up_question(sinusitis, 'Do you feel pressure or tenderness around your eyes, cheeks, or forehead?').
follow_up_question(food_poisoning, 'Did the symptoms start shortly after eating a particular meal?').
follow_up_question(food_poisoning, 'Have others who ate the same food become ill?').
follow_up_question(allergic_rhinitis, 'Do symptoms worsen during specific seasons or environments (e.g., around pets, dust)?').
follow_up_question(allergic_rhinitis, 'Are your eyes also itchy or watery?').
follow_up_question(constipation, 'How many days has it been since your last bowel movement?').
follow_up_question(constipation, 'Is your diet typically low in fiber?').

% --------------------------------------------------
% Answer Impact Logic
% answer_impact(DiseaseAtom, QuestionString, AnswerAtom (yes/no), AdjustmentValue).
% --------------------------------------------------
answer_impact(pneumonia, 'Is the cough producing colored phlegm (yellow/green)?', yes, 10).
answer_impact(bronchitis, 'Is the cough producing colored phlegm (yellow/green)?', yes, 5). % Assuming less indicative for bronchitis
answer_impact(pneumonia, 'Are you experiencing sharp chest pain, especially when breathing deeply?', yes, 15).
answer_impact(bronchitis, 'Are you experiencing sharp chest pain, especially when breathing deeply?', yes, -5). % Pain not typical for bronchitis
answer_impact(covid19, 'Have you experienced a recent loss of smell or taste?', yes, 20).
answer_impact(flu, 'Have you experienced a recent loss of smell or taste?', yes, -10). % Less common for flu than COVID
answer_impact(common_cold, 'Have you experienced a recent loss of smell or taste?', yes, -10). % Rare for common cold
answer_impact(dengue, 'Have you noticed any tiny red spots (petechiae) on your skin?', yes, 15).
answer_impact(dengue, 'Have you recently traveled to an area where Dengue is common?', yes, 10).
answer_impact(asthma, 'Does the shortness of breath worsen at night or with exercise?', yes, 10).
answer_impact(asthma, 'Do you have a personal or family history of allergies or eczema?', yes, 5).
answer_impact(migraine, 'Do you experience visual disturbances (aura) before the headache?', yes, 15).
answer_impact(migraine, 'Is the headache usually on one side of the head?', yes, 10).
answer_impact(appendicitis, 'Is the abdominal pain primarily in the lower right side?', yes, 20).
answer_impact(appendicitis, 'Does the pain worsen with movement or coughing?', yes, 10).
answer_impact(food_poisoning, 'Is the abdominal pain primarily in the lower right side?', yes, -10). % To differentiate from appendicitis
answer_impact(food_poisoning, 'Did the symptoms start shortly after eating a particular meal?', yes, 15).
answer_impact(food_poisoning, 'Have others who ate the same food become ill?', yes, 10).
answer_impact(urinary_tract_infection, 'Is there any blood visible in the urine?', yes, 10).
answer_impact(urinary_tract_infection, 'Do you have pain in your back or side (flank pain)?', yes, 10). % Could indicate kidney involvement
answer_impact(tuberculosis, 'Have you had unexplained weight loss recently?', yes, 10). % Question is duplicated
answer_impact(tuberculosis, 'Are you coughing up blood or blood-stained mucus?', yes, 15).
answer_impact(diabetes, 'Have you noticed any unexplained weight loss?', yes, 5). % Also a TB question, impact might differ
answer_impact(diabetes, 'Do cuts or sores seem slow to heal?', yes, 10).
answer_impact(anemia, 'Does your diet include iron-rich foods (like red meat, spinach)?', no, 10). % 'no' answer increases likelihood

% --------------------------------------------------
% Calculate Total Adjustment from Answers
% calculate_answer_adjustment(AnswerList, DiseaseAtom, TotalAdjustment).
% AnswerList is [(QuestionString, AnswerAtom (yes/no)), ...]
% --------------------------------------------------
calculate_answer_adjustment([], _, 0).
calculate_answer_adjustment([(Question, Answer) | RestAnswers], Disease, TotalAdjustment) :-
    ( answer_impact(Disease, Question, Answer, Adjustment) ->
        CurrentAdjustment = Adjustment
    ;   CurrentAdjustment = 0 % No specific impact defined for this Q/A for this Disease
    ),
    calculate_answer_adjustment(RestAnswers, Disease, RestAdjustment),
    TotalAdjustment is CurrentAdjustment + RestAdjustment.

% --------------------------------------------------
% Overall Matching Logic
% symptom_match(UserSymptomsList, UserRiskFactorsList, AnswerList, DiseaseAtom, FinalScore).
% UserSymptomsList: list of symptom atoms reported by user (e.g., ['fever', 'cough']).
% UserRiskFactorsList: list of risk factor atoms reported by user (e.g., ['smoking']).
% AnswerList: list of tuples (QuestionString, AnswerAtom) e.g., [('Are body aches severe?', yes)].
% DiseaseAtom: output variable for a potential disease.
% FinalScore: output variable for the calculated confidence score (0-100).
% --------------------------------------------------
symptom_match(UserSymptoms, UserRiskFactors, AnswerList, Disease, FinalScore) :-
    disease(Disease, DiseaseSymptomList),                % Get a disease and its typical symptoms/weights.
    total_weight(DiseaseSymptomList, TotalPossibleWeight),
    TotalPossibleWeight > 0,                             % Ensure total weight is positive to avoid division by zero.
    symptom_score(UserSymptoms, DiseaseSymptomList, MatchedSymptomScore), % Calculate score from matched symptoms.
    risk_factor_bonus(UserRiskFactors, Disease, RiskBonus),            % Calculate bonus from risk factors.
    calculate_answer_adjustment(AnswerList, Disease, AnswerAdjustment), % Calculate adjustment from follow-up answers.
    SymptomPercentMatch is (MatchedSymptomScore / TotalPossibleWeight) * 100,
    RawAdjustedScore is SymptomPercentMatch + RiskBonus + AnswerAdjustment,
    FinalScore is max(0.0, min(RawAdjustedScore, 100.0)). % Cap score between 0 and 100.
    % No cut here to allow findall to find all matching diseases.

% ------------------------
% Treatment Suggestions
% treatment(DiseaseAtom, ListOfTreatmentAtomsOrStrings).
% ------------------------
treatment(flu, ['rest', 'fluids', 'paracetamol for fever/pain']).
treatment(common_cold, ['hydration', 'steam_inhalation', 'rest', 'throat lozenges']).
treatment(covid19, ['isolation', 'rest', 'hydration', 'antipyretics (e.g., paracetamol)', 'monitor oxygen levels', 'seek medical help if breathing worsens']).
treatment(dengue, ['fluid_replacement (oral or IV)', 'monitor_platelet_count', 'paracetamol for fever (avoid NSAIDs like ibuprofen)']).
treatment(asthma, ['use prescribed inhaler (reliever/controller)', 'avoid known triggers', 'follow asthma action plan', 'bronchodilators']).
treatment(migraine, ['rest in a quiet, dark room', 'pain_relievers (e.g., ibuprofen, triptans if prescribed)', 'cold compress', 'avoid triggers']).
treatment(hypertension, ['lifestyle changes (diet, exercise)', 'medication (e.g., ACE_inhibitors, beta_blockers)', 'low_sodium_diet', 'stress management']).
treatment(diabetes, ['medication (e.g., insulin, metformin)', 'blood sugar monitoring', 'healthy diet (low sugar, controlled carbs)', 'regular exercise', 'foot care']).
treatment(pneumonia, ['antibiotics (if bacterial)', 'antivirals (if viral)', 'rest', 'hydration', 'oxygen_support (if severe)', 'fever reducers']).
treatment(typhoid, ['antibiotics', 'fluid_intake', 'rest', 'eat easily digestible food']).
treatment(chickenpox, ['calamine_lotion for itching', 'cool_baths with baking soda or oatmeal', 'antihistamines for itching', 'keep fingernails short', 'isolation to prevent spread']).
treatment(tuberculosis, ['course of anti_tb_drugs (typically multiple drugs for months)', 'good nutrition', 'rest', 'regular medical follow-up']).
treatment(bronchitis, ['rest', 'hydration', 'humidifier or steam inhalation', 'avoid smoke and irritants', 'cough_suppressants (if cough is very disruptive and non-productive)', 'bronchodilators (if wheezing)']).
treatment(hepatitis_b, ['antiviral medication (for chronic cases)', 'avoid_alcohol', 'regular_monitoring of liver function', 'vaccination for prevention']).
treatment(urinary_tract_infection, ['antibiotics', 'increased hydration', 'cranberry_juice (evidence is mixed, but often suggested)', 'avoid irritants']).
treatment(anemia, ['iron_supplements (if iron-deficiency anemia)', 'iron_rich_diet', 'vitamin B12 or folate supplements (if deficient)', 'treat_underlying_cause of blood loss or malabsorption']).
treatment(sinusitis, ['nasal_decongestant_spray (short-term use)', 'saline nasal irrigation', 'steam_inhalation', 'pain relievers', 'antibiotics (if bacterial and persistent)']).
treatment(food_poisoning, ['oral_rehydration_salts or fluids to prevent dehydration', 'rest', 'bland diet (e.g., BRAT diet - bananas, rice, applesauce, toast) once nausea subsides', 'avoid dairy, fatty, or spicy foods initially']).
treatment(allergic_rhinitis, ['antihistamines', 'nasal_corticosteroid_spray', 'allergen_avoidance', 'decongestants (short-term)']).
treatment(constipation, ['increase dietary_fiber', 'increase_fluid_intake', 'regular_exercise', 'stool_softeners or laxatives (if needed, consult doctor for prolonged use)']).
treatment(appendicitis, ['surgery (appendectomy)', 'antibiotics before and possibly after surgery']).

% ------------------------
% Advice Generator
% advice(DiseaseAtom, AdviceString).
% Generic advice based on severity is provided by clauses at the end.
% Specific advice takes precedence.
% ------------------------
advice(diabetes, 'Maintain a healthy lifestyle, monitor your blood sugar regularly, and follow your prescribed diet and medication plan. Pay attention to foot care.').
advice(hypertension, 'Reduce salt intake, engage in regular physical activity, manage stress, monitor blood pressure regularly, and take medications as prescribed. Avoid alcohol and smoking.').
advice(asthma, 'Identify and avoid your asthma triggers. Always carry your reliever inhaler and use your controller inhaler as prescribed. Follow your asthma action plan.').
advice(covid19, 'Isolate yourself to prevent spread, rest, stay hydrated, and use paracetamol for fever. Monitor symptoms, especially breathing, and seek medical attention if they worsen or if you have risk factors for severe disease.').
advice(dengue, 'Rest and drink plenty of fluids (water, ORS). Use paracetamol for fever and pain, but AVOID aspirin or ibuprofen as they can increase bleeding risk. Monitor for warning signs (severe abdominal pain, persistent vomiting, bleeding, lethargy) and seek urgent medical care if they appear.').
advice(migraine, 'At the first sign of a migraine, rest in a quiet, dark room. Take your prescribed migraine medication. A cold pack on your forehead may help. Identify and avoid your triggers.').
advice(pneumonia, 'Take the full course of any prescribed antibiotics. Get plenty of rest and drink lots_of_fluids. Use a humidifier or take steamy showers to help with breathing.').
advice(typhoid, 'Complete the prescribed antibiotic course. Drink plenty of fluids and eat easily digestible foods. Maintain good personal hygiene to prevent spread.').
advice(tuberculosis, 'Adhere strictly to your long-term medication schedule. Eat a balanced, nutrient-rich diet to support recovery. Attend all follow-up appointments.').
advice(hepatitis_b, 'Avoid alcohol completely to protect your liver. Take antiviral medications if prescribed. Ensure regular medical check-ups to monitor liver health. Practice safe sex and avoid sharing needles.').
advice(anemia, 'If diagnosed with iron-deficiency anemia, take iron supplements as prescribed and eat iron-rich foods like spinach, red meat, and lentils. Address any underlying causes of blood loss.').
advice(allergic_rhinitis, 'Try to identify and avoid your allergens (e.g., pollen, dust mites, pet dander). Use antihistamines or nasal sprays as recommended. Keep your home environment clean.').
advice(food_poisoning, 'Focus on staying hydrated by drinking small, frequent sips of water or rehydration solutions. Gradually reintroduce bland foods. Rest. Wash hands thoroughly to prevent spread.').
advice(urinary_tract_infection, 'Drink plenty of water to help flush bacteria. Complete the full course of antibiotics if prescribed. Urinate frequently and after intercourse. Maintain good genital hygiene.').
advice(constipation, 'Increase your intake of fiber-rich foods (fruits, vegetables, whole grains), drink plenty of water, and engage in regular physical activity. Establish regular bowel habits.').
advice(sinusitis, 'Use saline nasal rinses or sprays. Inhale steam. Apply warm compresses to your face. Get plenty of rest. If symptoms are severe or persist, consult a doctor as antibiotics may be needed for bacterial sinusitis.').
advice(appendicitis, 'This is a medical emergency. Seek immediate surgical consultation. Do not eat or drink anything while waiting for medical assessment.').
advice(bronchitis, 'Get plenty of rest, drink warm fluids, and use a humidifier. Avoid lung irritants like smoke. Over-the-counter pain relievers and cough medicine may provide some relief.').
advice(chickenpox, 'Focus on relieving itching with cool baths, calamine lotion, and antihistamines. Keep fingernails short to prevent skin infections from scratching. Stay home to avoid spreading the virus.').
advice(common_cold, 'Get plenty of rest, drink fluids like water and warm tea, and use a humidifier or steam inhalation. Gargling with salt water can soothe a sore throat. Over-the-counter remedies may help with symptoms.').
advice(flu, 'Rest at home, drink plenty of fluids, and take over-the-counter medications for fever and aches (e.g., paracetamol, ibuprofen). Antiviral medications may be an option if started early, especially for high-risk individuals.').

% Generic advice based on severity (these act as fallbacks if no specific advice for a disease is found above)
advice(Disease, 'This condition is considered severe. Seek immediate medical attention!') :- severe(Disease), !.
advice(Disease, 'This condition is generally moderate. It is advisable to consult a doctor for proper diagnosis and management.') :- moderate(Disease), !.
advice(Disease, 'This condition is generally mild. Monitor your symptoms, rest, and take supportive care. Consult a doctor if symptoms worsen or persist.') :- mild(Disease), !.
advice(_, 'Please consult a healthcare professional for an accurate diagnosis and advice tailored to your specific situation. Follow general medical guidance.'). % Ultimate fallback