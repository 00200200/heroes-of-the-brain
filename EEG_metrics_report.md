# EEG Metrics Calculation Report

## 1. Preprocessing
- EEG data is collected from 8 channels: **F3, F4, C3, C4, P3, P4, O1, O2** (according to the international 10-20 system).
- For each channel, the signal is filtered and the bandpower (RMS) is calculated for:
  - **Theta**: 4–8 Hz
  - **Alpha**: 8–13 Hz
  - **Beta**: 13–30 Hz

## 2. Focus (Concentration)
- **Formula:**
  
  $$
  \text{Focus} = \frac{\text{mean beta (F3,F4,C3,C4)}}{\text{mean theta (F3,F4,C3,C4)}}
  $$
- The result is adaptively normalized to the 0–100 range based on observed min/max values (the model dynamically adjusts the range).

## 3. Stress
- **Formula:**
  
  $$
  \text{Stress} = \log(\text{alpha}_{F4}) - \log(\text{alpha}_{F3}) + \frac{\text{mean beta (F3,F4)}}{\text{mean alpha (F3,F4)}}
  $$
- The result is normalized to the 0–100 range.

## 4. Tiredness (Fatigue)
- **Formula:**
  
  $$
  \text{Tiredness} = \frac{\text{mean theta (P3,P4,O1,O2)} + \text{mean alpha (P3,P4,O1,O2)}}{\text{total power (P3,P4,O1,O2)}}
  $$
- The result is normalized to the 0–100 range.

## 5. Buffering and Window
- All metrics are calculated based on the signal from the last 2 minutes (buffer of 24 samples, each every 5 seconds).

---

### Channel and Band Explanation
- **Channels** (e.g., P3, O1) are electrode locations on the scalp (see the 10-20 system diagram).
- **Bands** (alpha, beta, theta, gamma) are frequency ranges in the EEG signal.
- Bandpower is calculated for each channel and then averaged for groups of channels to get the final metric.

---

**This approach is based on EEG research standards and is ready for further calibration and development.**
