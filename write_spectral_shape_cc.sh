#!/bin/bash
# usage: ./spectral_shape.sh <input_audio_file>

# write_spectral_shape_cc.sh - Convert audio descriptors to MIDI CC using SuperCollider & FLUCOMA
# Copyright (c) 2025 John Matter
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
#
# This project also uses FLUCOMA, which is licensed under the BSD 3-Clause License.

INPUT_AUDIO="$1"
# if output not specified, use input file name with .midi extension
if [ -z "$2" ]; then
    OUTPUT_MIDI="${INPUT_AUDIO%.*}".midi
else
    OUTPUT_MIDI="$2"
fi
TEMP_CSV="temp_midi.csv"
TEMP_SCD="process_audio.scd"
SAMPLE_RATE=30

# Create a temporary SuperCollider script
cat > "$TEMP_SCD" <<EOL
s.waitForBoot {
    var src = Buffer.read(s, "$INPUT_AUDIO");
    var specbuf = Buffer(s);

    FluidBufSpectralShape.processBlocking(s, src, features: specbuf);
    
    specbuf.loadToFloatArray(action: { |fa|
        var spec = fa.clump(specbuf.numChannels);
        var sampleRate = $SAMPLE_RATE;
        var step = (spec.size / (src.duration * sampleRate)).floor.asInteger;
        var selectedFrames = (0, step .. spec.size - 1);
        
        // Extract min/max for normalization
        var minVals = spec.flop.collect(_.minItem);
        var maxVals = spec.flop.collect(_.maxItem);
        
        var normalized = selectedFrames.collect { |i|
            spec[i].collect { |val, j|
                ((val - minVals[j]) / (maxVals[j] - minVals[j]) * 127).clip(0, 127).asInteger;
            }
        };
        
        // SpectralShape parameter names
        var paramNames = [
            "Centroid", "Spread", "Skewness", "Kurtosis", 
            "Rolloff", "Flatness", "Crest", "MFCC1", 
            "MFCC2", "MFCC3", "MFCC4", "MFCC5", 
            "MFCC6", "MFCC7"
        ];
        
        // Create JSON representation of parameter mapping (single line)
        var jsonMap = "{" ++ 
            paramNames.collect { |name, i|
                "\"" ++ i ++ "\":\"" ++ name ++ "\"";
            }.join(",") ++ 
            "}";
        
        // Write CSV MIDI data
        File("$TEMP_CSV".standardizePath, "w").write(
            "0, 0, Header, 1, 1, 480\n" ++  // Standard MIDI header
            "1, 0, Start_track\n" ++
            "1, 0, Title_t, \"Spectral shape (SR=" ++ sampleRate ++ "Hz): $INPUT_AUDIO\"\n" ++
            
            // Add JSON mapping as a single text event (on a single line)
            "1, 0, Text_t, \"" ++ jsonMap.replace("\"", "\"\"") ++ "\"\n" ++
            
            normalized.collect { |frame, time|
                frame.collect { |val, cc|
                    "1, " ++ (time * sampleRate).asInteger ++ ", Control_c, 1, " ++ (cc) ++ ", " ++ val ++ "\n";
                }.join;
            }.join ++
            "1, " ++ ((normalized.size - 1) * sampleRate).asInteger ++ ", End_track\n" ++
            "0, 0, End_of_file\n"
        );
        
        s.quit;
    });
    0.exit;
};
EOL

# Run SuperCollider script to generate CSV
sclang "$TEMP_SCD"

# Convert CSV to MIDI
csvmidi "$TEMP_CSV" "$OUTPUT_MIDI"

# Clean up
rm -f "$TEMP_CSV" "$TEMP_SCD"

echo "MIDI file created: $OUTPUT_MIDI"
