# -*- coding: utf-8 -*-
import sys
import os
import shutil

ROOT_DIR = os.path.abspath(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT_DIR)

from audioclipcutter.core import AudioClipCutter

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
TESTS_DATA_DIR = os.path.join(TESTS_DIR, 'data')

def findFileRecursively(filename, directory):
    for root, dirs, files in os.walk(directory):
        for f in files:
            if f == filename:
                return os.path.join(root, f)

    return None

def joinDataDir(filename):
    return os.path.join(TESTS_DATA_DIR, filename)

class TestAudioClipCutter:
    def setup_class(self):
        filename = 'ffmpeg.exe' if sys.platform == "win32" else 'ffmpeg'

        # First: looks for the executable recursively in ROOT_DIR
        ffmpegPath = findFileRecursively(filename, ROOT_DIR)

        if not ffmpegPath:
            # Second: looks for the executable in PATH
            ffmpegPath = shutil.which(filename)

        self.ffmpegPath = ffmpegPath
        self.audioPath = os.path.join(TESTS_DATA_DIR, 'synthesized_speech.mp3')
        self.specsPath = os.path.join(TESTS_DATA_DIR, 'synthesized_speech.txt')
    def test_ffmpegPath(self):
        assert self.ffmpegPath, "`%s` not found." % self.ffmpegPath

    def test_audio_extract(self):
        extractor = AudioClipCutter(self.audioPath, self.ffmpegPath)
        extractor.extractClips(self.specsPath, TESTS_DATA_DIR)

        for extractedClipPath, expectedClipPath in zip(
            [joinDataDir("clip%d.mp3" % i) for i in range(1, 7)],
            [joinDataDir("expected_clip%d.mp3" % i) for i in range(1, 7)]):

            assert os.path.isfile(extractedClipPath), \
                "'%s' not found" % extractedClipPath

            f_extracted = open(extractedClipPath, 'rb')
            f_expected = open(expectedClipPath, 'rb')

            # Compare files
            try:
                assert f_extracted.read() == f_expected.read(), \
                    "'%s' It doesn't match expected data" % expectedClipPath
            except(AssertionError) as e:
                f_expected.close()
                f_extracted.close()

                os.unlink(extractedClipPath)

            if os.path.isfile(extractedClipPath):
                os.unlink(extractedClipPath)

    def test_audio_extract_with_zip_archiving(self):
        extractor = AudioClipCutter(self.audioPath, self.ffmpegPath)
        extractor.extractClips(self.specsPath, TESTS_DATA_DIR, zipOutput=True)

        extractedZipPath = joinDataDir('synthesized_speech_clips.zip')
        expectedZipPath = joinDataDir('expected_archive.zip')

        assert os.path.isfile(extractedZipPath), \
            "'%s' not found" % extractedZipPath

        f_extracted = open(extractedZipPath, 'rb')
        f_expected = open(expectedZipPath, 'rb')

        try:
            assert f_extracted.read() == f_expected.read(), \
                "'%s' It doesn't match expected data" % extractedZipPath
        except(AssertionError) as e:
            f_expected.close()
            f_extracted.close()

            os.unlink(extractedZipPath)