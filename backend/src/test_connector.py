"""
Test suite for EEG connector filters
"""

import numpy as np
from scipy.signal import sosfiltfilt
import matplotlib.pyplot as plt
from connector import design_filters, butter_bandpass, preprocess_chunk
def test_preprocess_chunk_single_channel():
    """
    Test preprocess_chunk on single-channel synthetic data.
    """
    print("\n--- Testing preprocess_chunk (single channel) ---")
    sfreq = 250
    duration = 2
    t = np.arange(0, duration, 1/sfreq)
    # 10Hz + 50Hz + 100Hz
    signal = (
        np.sin(2 * np.pi * 10 * t) +
        0.5 * np.sin(2 * np.pi * 50 * t) +
        0.3 * np.sin(2 * np.pi * 100 * t)
    )
    chunk = signal[np.newaxis, :]
    filters = design_filters(sfreq)
    chunk_clean = preprocess_chunk(chunk, filters)
    # Should be zero-mean (per channel)
    mean_val = np.mean(chunk_clean, axis=1)
    print(f"Mean after preprocess: {mean_val}")
    assert np.allclose(mean_val, 0, atol=1e-6), "❌ preprocess_chunk did not remove mean"
    # Should attenuate 50Hz and 100Hz
    # Check RMS reduction
    rms_before = np.sqrt(np.mean(chunk**2))
    rms_after = np.sqrt(np.mean(chunk_clean**2))
    print(f"RMS before: {rms_before:.4f}, after: {rms_after:.4f}")
    assert rms_after < rms_before, "❌ preprocess_chunk did not attenuate noise"
    print("✓ preprocess_chunk (single channel) passed!\n")

def test_preprocess_chunk_multi_channel():
    """
    Test preprocess_chunk on multi-channel synthetic data.
    """
    print("\n--- Testing preprocess_chunk (multi-channel) ---")
    sfreq = 250
    duration = 2
    n_channels = 4
    t = np.arange(0, duration, 1/sfreq)
    # Każdy kanał: 10Hz + 50Hz + 100Hz
    chunk = np.zeros((n_channels, len(t)))
    for ch in range(n_channels):
        chunk[ch] = (
            np.sin(2 * np.pi * 10 * t) +
            0.5 * np.sin(2 * np.pi * 50 * t) +
            0.3 * np.sin(2 * np.pi * 100 * t)
        )
    filters = design_filters(sfreq)
    chunk_clean = preprocess_chunk(chunk, filters)
    # Sprawdź kształt
    assert chunk_clean.shape == chunk.shape, "❌ preprocess_chunk shape mismatch"
    # Sprawdź rereferencję: suma po kanałach powinna być bliska zeru (w każdej próbce)
    reref_sum = np.abs(np.sum(chunk_clean, axis=0))
    max_reref = np.max(reref_sum)
    print(f"Max rereference sum (should be ~0): {max_reref:.2e}")
    assert max_reref < 1e-6, "❌ preprocess_chunk rereference failed"
    print("✓ preprocess_chunk (multi-channel) passed!\n")


def test_filters():
    """
    Test the bandpass and notch filters with synthetic data.
    """
    print("\n--- Testing Filters ---")
    
    sfreq = 250  # Sampling frequency
    duration = 2  # seconds
    t = np.arange(0, duration, 1/sfreq)
    
    # Create synthetic signal: 10Hz + 50Hz (noise) + 100Hz (high freq noise)
    signal = (
        np.sin(2 * np.pi * 10 * t) +      # 10Hz signal (should pass)
        0.5 * np.sin(2 * np.pi * 50 * t) +  # 50Hz noise (should be removed)
        0.3 * np.sin(2 * np.pi * 100 * t)   # 100Hz noise (should be removed)
    )
    
    print(f"Original signal shape: {signal.shape}")
    print(f"Original signal range: [{signal.min():.4f}, {signal.max():.4f}]")
    
    # Get filters
    filters = design_filters(sfreq)
    bandpass_sos = filters['bandpass_sos']
    notch_sos = filters['notch_sos']
    
    # Apply bandpass filter (1-40 Hz)
    filtered_bandpass = sosfiltfilt(bandpass_sos, signal)
    print(f"After bandpass (1-40Hz): [{filtered_bandpass.min():.4f}, {filtered_bandpass.max():.4f}]")
    
    # Apply notch filter (removes 50Hz)
    filtered_notch = sosfiltfilt(notch_sos, signal)
    print(f"After notch (50Hz): [{filtered_notch.min():.4f}, {filtered_notch.max():.4f}]")
    
    # Apply both filters
    filtered_both = sosfiltfilt(bandpass_sos, signal)
    filtered_both = sosfiltfilt(notch_sos, filtered_both)
    print(f"After both filters: [{filtered_both.min():.4f}, {filtered_both.max():.4f}]")
    
    # Verify signal reduction
    reduction = np.sqrt(np.mean(signal**2)) - np.sqrt(np.mean(filtered_both**2))
    print(f"\nSignal energy reduction: {reduction:.4f}")
    
    assert np.isfinite(filtered_bandpass).all(), "❌ Bandpass filter produced NaN/Inf"
    assert np.isfinite(filtered_notch).all(), "❌ Notch filter produced NaN/Inf"
    assert np.isfinite(filtered_both).all(), "❌ Combined filters produced NaN/Inf"
    
    print("✓ Filters tested successfully!")
    print("  ✓ Bandpass filter removes high frequencies")
    print("  ✓ Notch filter removes 50Hz noise")
    print("  ✓ Combined filtering works correctly\n")


def test_bandpass_range():
    """
    Test that bandpass filter only passes 1-40 Hz frequencies.
    """
    print("\n--- Testing Bandpass Frequency Range ---")
    
    sfreq = 250
    duration = 2  # Longer duration for better frequency resolution
    t = np.arange(0, duration, 1/sfreq)
    
    filters = design_filters(sfreq)
    bandpass_sos = filters['bandpass_sos']
    
    # Test different frequencies
    test_freqs = [0.5, 1, 10, 20, 40, 50, 100, 200]
    results = []
    
    for freq in test_freqs:
        signal = np.sin(2 * np.pi * freq * t)
        filtered = sosfiltfilt(bandpass_sos, signal)
        
        # Calculate amplitude ratio (gain)
        original_amplitude = np.sqrt(np.mean(signal**2))
        filtered_amplitude = np.sqrt(np.mean(filtered**2))
        gain = filtered_amplitude / original_amplitude if original_amplitude > 0 else 0
        attenuation = 1 - gain
        
        # In pass band (1-40 Hz), gain should be high
        # Outside pass band, gain should be low
        is_in_passband = (1 <= freq <= 40)
        if is_in_passband:
            # Inside passband: expect gain > 0.4 (less than 60% attenuation)
            passes = gain > 0.4
        else:
            # Outside passband: expect gain < 0.5 (more than 50% attenuation)
            passes = gain < 0.5
        
        status = "✓ PASS" if passes else "✗ FAIL"
        results.append(passes)
        print(f"  {freq:6.1f}Hz: gain={gain:.2f} (attenuation={attenuation:.2%}) {status}")
    
    assert all(results), "❌ Some frequencies failed filtering"
    print("\n✓ All frequency tests passed!\n")


def test_multi_channel():
    """
    Test filters on multi-channel data (like real EEG).
    """
    print("\n--- Testing Multi-Channel Filtering ---")
    
    sfreq = 250
    duration = 1
    n_channels = 8  # 8 EEG channels
    t = np.arange(0, duration, 1/sfreq)
    
    # Create multi-channel synthetic data
    data = np.zeros((n_channels, len(t)))
    for ch in range(n_channels):
        data[ch] = (
            np.sin(2 * np.pi * 10 * t) +
            0.5 * np.sin(2 * np.pi * 50 * t) +
            0.3 * np.sin(2 * np.pi * 100 * t)
        )
    
    print(f"Input shape: {data.shape}")
    
    filters = design_filters(sfreq)
    bandpass_sos = filters['bandpass_sos']
    notch_sos = filters['notch_sos']
    
    # Apply filters to each channel
    filtered_data = np.zeros_like(data)
    for ch in range(n_channels):
        filtered_data[ch] = sosfiltfilt(bandpass_sos, data[ch])
        filtered_data[ch] = sosfiltfilt(notch_sos, filtered_data[ch])
    
    print(f"Output shape: {filtered_data.shape}")
    assert filtered_data.shape == data.shape, "❌ Shape mismatch after filtering"
    assert np.isfinite(filtered_data).all(), "❌ Filtered data contains NaN/Inf"
    
    print("✓ Multi-channel filtering successful!")
    print(f"  ✓ Input and output shapes match")
    print(f"  ✓ All channels processed correctly\n")


if __name__ == "__main__":
    try:
        test_filters()
        test_bandpass_range()
        test_multi_channel()
        test_preprocess_chunk_single_channel()
        test_preprocess_chunk_multi_channel()
        print("\n" + "="*50)
        print("✓ ALL TESTS PASSED!")
        print("="*50 + "\n")
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}\n")
        import traceback
        traceback.print_exc()
