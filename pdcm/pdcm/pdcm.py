"""Parses DICOM files.
"""
import datetime
import os
import struct
import tempfile
import warnings

import numpy as np
import matplotlib.pyplot


ATTRIBUTE = {}
ATTRIBUTE[0x02] = {0x0000: 'FileMetaInformationGroupLength',
                   0x0001: 'FileMetaInformationVersion',
                   0x0002: 'MediaStorageSOPClassUID',
                   0x0003: 'MediaStorageSOPInstanceUID',
                   0x0010: 'TransferSyntaxUID',
                   0x0012: 'ImplementationClassUID',
                   0x0013: 'ImplementationVersionName',
                   0x0016: 'SourceApplicationEntityTitle',
                   }
ATTRIBUTE[0x08] = {0x0005: 'SpecifiedCharacterSet',
                   0x0008: 'ImageType',
                   0x0016: 'SOPCaseUID',
                   0x0018: 'SOPInstanceUID',
                   0x0020: 'StudyDate',
                   0x0021: 'SeriesDate',
                   0x0022: 'AcquisitionDate',
                   0x0023: 'ContentDate',
                   0x0024: 'OverlayDate',
                   0x0025: 'CurveDate',
                   0x002a: 'AcquisitionDatetime',
                   0x0030: 'StudyTime',
                   0x0031: 'SeriesTime',
                   0x0032: 'AcquisitionTime',
                   0x0033: 'ContentTime',
                   0x0050: 'AccessionNumber',
                   0x0060: 'Modality',
                   0x0070: 'Manufacturer',
                   0x0080: 'InstitutionName',
                   0x0090: 'ReferringPhysicianName',
                   0x1050: 'PerformingPhysicianName',
                   0x1090: 'ManufacturerModelName',
                   0x1155: 'ReferencedSOPInstanceUID',
                   0x1010: 'StationName',
                   0x1030: 'StudyDescription',
                   0x103e: 'SeriesDescription',
                   0x1070: 'OperatorName',
                   0x1110: 'ReferencedStudySequence',
                   0x1111: 'ReferencedPerformedProcedureStepSequence',
                   0x1120: 'ReferencedPatientSequence',
                   0x1140: 'ReferencedImageSequence',
                   }
ATTRIBUTE[0x0010] = {0x0010: 'PatientName',
                     0x0020: 'PatientID',
                     0x0030: 'PatientBirthDate',
                     0x0040: 'PatientSex',
                     0x1010: 'PatientAge',
                     0x1030: 'PatientWeight',
                     0x21b0: 'AdditionalPatientHistory',
                     0x21d0: 'LastMenstrualDate',
        }
ATTRIBUTE[0x0012] = {0x0062: 'PatientIdentityRemoved',
                     0x0063: 'De-identificationMethod',
        }
ATTRIBUTE[0x0018] = {0x0015: 'BodyPartExamined',
                     0x0020: 'ScanningSequence',
                     0x0021: 'SequenceVariant',
                     0x0022: 'ScanOptions',
                     0x0023: 'MRAcquisitionType',
                     0x0024: 'SequenceName',
                     0x0025: 'AngioFlag',
                     0x0050: 'SliceThickness',
                     0x0060: 'KVP',
                     0x0080: 'RepetitionTime',
                     0x0081: 'EchoTime',
                     0x0083: 'NumberOfAverages',
                     0x0084: 'ImagingFrequency',
                     0x0085: 'ImagedNucleus',
                     0x0086: 'ImageNumbers',
                     0x0087: 'MagneticFieldStrength',
                     0x0088: 'SpacingBetweenSlices',
                     0x0089: 'NumberOfPhaseEncodingSteps',
                     0x0091: 'EchoTrainLength',
                     0x0093: 'PercentSampling',
                     0x0094: 'PercentPhaseFieldOfView',
                     0x0095: 'PixelBandwidth',
                     0x1000: 'DeviceSerialNumber',
                     0x1020: 'SoftwareVersion',
                     0x1030: 'ProtocolName',
                     0x1088: 'HeartRate',
                     0x1090: 'CardiacNumberOfImages',
                     0x1094: 'TriggerWindow',
                     0x1100: 'ReconstructionWindow',
                     0x1110: 'DistanceSourceToDetector',
                     0x1111: 'DistanceSourceToPatient',
                     0x1150: 'ExposureTime',
                     0x1151: 'XRayTubeCurrent',
                     0x1152: 'Exposure',
                     0x1160: 'FilterType',
                     0x1190: 'FocalSpot',
                     0x1250: 'ReceiveCoilName',
                     0x1251: 'TransmitCoilName',
                     0x1310: 'AcquisitionMatrix',
                     0x1312: 'InPlanePhaseEncodingDirection',
                     0x1314: 'FlipAngle',
                     0x1315: 'VariableFlipAngleFlag',
                     0x1316: 'SAR',
                     0x1318: 'dBdt',
                     0x5100: 'PatientPosition',
        }
ATTRIBUTE[0x0020] = {
        0x000d: 'StudyInstanceUID',
        0x000e: 'SeriesInstanceUID',
        0x0010: 'StudyID',
        0x0011: 'SeriesNumber',
        0x0012: 'AcquisitionNumber',
        0x0013: 'InstanceNumber',
        0x0020: 'PatientOrientation',
        0x0030: 'ImagePosition',
        0x0032: 'ImagePositionPatient',
        0x0035: 'ImageOrientation',
        0x0037: 'ImageOrientationPatient',
        0x0052: 'FrameOfReferenceUID',
        0x0200: 'SynchronizationFrameOfReferenceUID',
        0x1002: 'ImagesInAcquisition',
        0x1040: 'PositionReferenceIndicatoPositionReferenceIndicator',
        0x1041: 'SliceLocation',
        0x4000: 'ImageComments',
        }
ATTRIBUTE[0x0028] = {0x0002: 'SamplesPerPixel',
                     0x0004: 'PhotometricInterpretation',
                     0x0010: 'Rows',
                     0x0011: 'Columns',
                     0x0030: 'PixelSpacing',
                     0x0100: 'BitsAllocated',
                     0x0101: 'BitsStored',
                     0x0102: 'HighBit',
                     0x0103: 'PixelRepresentation',
                     0x0106: 'SmallestImagePixelValue',
                     0x0107: 'LargestImagePixelValue',
                     0x0120: 'PixelPaddingValue',
                     0x0303: 'LongitudinalTemporalInformationModified',
                     0x1050: 'WindowCenter',
                     0x1051: 'WindowWidth',
                     0x1052: 'RescaleIntercept',
                     0x1053: 'RescaleSlope',
                     0x1054: 'RescaleType',
                     0x1055: 'WindowCenterWidthExplanation',
                     0x2110: 'LossyImageCompression',
                     0x2112: 'LossyImageCompressionRatio',
        }
ATTRIBUTE[0x0032] = {0x000a: 'StudyStatusID',
                     0x1000: 'ScheduledStudyStartDate',
                     0x1001: 'ScheduledStudyStartTime',
                     0x1021: 'ScheduledStudyLocationAETitle',
                     0x1032: 'RequestingPhysician',
                     0x1060: 'RequestedProcedureDescription',
                     0x4000: 'StudyComments',
        }
ATTRIBUTE[0x0038] = {
        0x0020: 'AdmittingDate',
        }
ATTRIBUTE[0x0040] = {0x0002: 'ScheduledProcedureStepStartDate',
                     0x0004: 'ScheduledProcedureStepEndDate',
                     0x0244: 'PerformedProcedureStepStartDate',
                     0x0245: 'PerformedProcedureStepStartTime',
                     0x0254: 'PerformedProcedureStepDescription',
                     0x0275: 'RequestedAttributesSequence',
                     0x2016: 'PlacerOrderNumber/ImagingServiceRequest',
                     0x2017: 'FillerOrderNumber/ImagingServiceRequest',
                     0xa075: 'VerifyingObserverName',
                     0xa123: 'PersonName',
                     0xa124: 'UID',
        }
ATTRIBUTE[0x0070] = {0x0084: 'ContentCreatorName',
        }
ATTRIBUTE[0x0088] = {0x0140: 'StorageMediaFileSetUID',
        }
ATTRIBUTE[0x3006] = {0x0024: 'ReferencedFrameOfReferenceUID',
                     0x00c2: 'RelatedFrameOfReferenceUID',
        }
ATTRIBUTE[0x7fe0] = {0x0010: 'PixelData',
        }


class DicomTag(object):
    """Represents a single DICOM tag.
    """

    def __init__(self, group=None, elem=None, vr=None, value=None,
                 bytelen=None, offset=None, name=None):
        """
        Parameters
        ----------
        group, elem : int
            Uniquely identifies a DICOM tag.
        vr : str
            Value representation, a two-char string.
        value : string, int, or float
            Interpreted value for the tag
        bytelen : int
            Length of tag value in bytes, not the length of the tag itself.
        offset : int
            Byte position of the tag in the file.
        name : str
            Name of the DICOM tag.
        """
        self.group = group
        self.elem = elem
        self.vr = vr
        self.name = name
        self.value = value
        self.offset = offset
        self.bytelen = bytelen

    def __str__(self):
        if self.vr == 'DA':
            valstr = self.value.__str__()
        elif self.vr == 'OW':
            valstr = '(Pixel data goes here)'
        else:
            valstr = self.value.__str__()
        msg = "@{0:8} ({1:04x},{2:04x}) {3:2} {4:30} # {5:6}, {6}"
        msg = msg.format(self.offset,
                         self.group,
                         self.elem,
                         self.vr,
                         valstr,
                         self.bytelen,
                         self.name)
        return msg

    @staticmethod        
    def parse(fptr):
        """Parse a single tag.

        Parameters
        ----------
        fptr : file object
            Points to starting byte for a single tag.
        """
        offset = fptr.tell()
        read_buffer = fptr.read(8)
        group, elem, VR, length = struct.unpack('<HH2sH', read_buffer)
        VR = VR.decode('utf-8')

        if VR in ['OB', 'OW', 'OF', 'SQ', 'UN']:
            # 11_05pu, section 7.1.2
            # The last length field is to be ignored.
            read_buffer = fptr.read(4)
            length, = struct.unpack('<I', read_buffer)
            if VR == 'OB':
                read_buffer = fptr.read(length)
                value = struct.unpack('<BB', read_buffer)
            elif VR == 'UN':
                value = fptr.read(length)
            elif VR == 'OW':
                # Just raw data.
                if length == 2**32 - 1:
                    # Must be an error, too much data.
                    value = fptr.read()
                else:
                    value = fptr.read(length)
            elif VR == 'SQ':
                value = fptr.read(length)
                value = '(Sequence data)'
            else:
                msg = "Unhandeled case ({0:x},{1:x}), {2} length={3}"
                msg = msg.format(group, elem, VR, length)
                raise NotImplementedError(msg)

        elif length == 0:
            value = None
        elif VR in ['UL']:
            read_buffer = fptr.read(length)
            value, = struct.unpack('<I', read_buffer)
        elif VR in ['SS']:
            # int16
            read_buffer = fptr.read(length)
            value, = struct.unpack('<h', read_buffer)
        elif VR in ['AE', 'AS', 'CS', 'DS', 'IS', 'LO', 'LT', 'PN', 'UI', 'SH']:
            read_buffer = fptr.read(length)
            value = read_buffer.decode('utf-8').strip(chr(0))
        elif VR == 'DA':
            # A date of the form YYYMMDD
            read_buffer = fptr.read(length)
            value = read_buffer.decode('utf-8').strip()
            year = int(value[0:4])
            month = int(value[4:6])
            day = int(value[6:8])
            value = datetime.date(year, month, day)
        elif VR == 'DT':
            # A date of the form YYYMMDD
            read_buffer = fptr.read(length)
            value = read_buffer.decode('utf-8').strip()
            year = int(value[0:4])
            month = 1
            day = 1
            hours = 0
            minutes = 0
            seconds = 0
            msecs = 0
            delta = datetime.timedelta(days=0)
            if length > 21:
                plusminus = -1 if value[21] == '-' else 1
                hours = int(value[22:24])
                minutes = int(value[24:26])
                seconds = hours * 3600 + minutes * 60
                delta = plusminus * datetime.timedelta(seconds=seconds)
            if length > 15:
                msecs = float(value[15:21]) / 1000000.
            if length > 12:
                seconds = int(value[12:14])
            if length > 10:
                minutes = int(value[10:12])
            if length > 8:
                hours = int(value[8:10])
            if length > 6:
                day = int(value[6:8])
            if length > 4:
                month = int(value[4:6])
            value = datetime.datetime(year, month, day, hours, minutes,
                                      seconds, msecs) + delta
        elif VR == 'TM':
            # A time of the form HHMMSS.FFFFFF
            if length == 0:
                value = None
            else:
                minutes = 0
                seconds = 0
                msecs = 0
                read_buffer = fptr.read(length)
                value = read_buffer.decode('utf-8').strip()
                hours = int(value[0:2])
                if length > 7:
                    msecs = int(value[7:13])
                if length > 4:
                    seconds = int(value[4:6])
                if length > 2:
                    minutes = int(value[2:4])
                value = datetime.time(hours, minutes, seconds, msecs)
        elif VR in ['US']:
            read_buffer = fptr.read(length)
            if length == 2:
                value, = struct.unpack('<H', read_buffer)
            elif length == 8:
                warnings.warn('Bad length ({0}) for VR "US"'.format(length))
                value, = struct.unpack('<Q', read_buffer)
        else:
            msg = "Unhandeled VR ({0:x},{1:x}), {2} length={3}"
            msg = msg.format(group, elem, VR, length)
            raise NotImplementedError(msg)

        try:
            name = ATTRIBUTE[group][elem]
        except KeyError:
            if group % 2 == 1:
                name = 'Unknown tag & data'
            else:
                msg = "Unhandeled case ({0:x},{1:x}), {2} length={3}"
                msg = msg.format(group, elem, VR, length)
                raise NotImplementedError(msg)

        tag = DicomTag(group=group,
                       elem=elem,
                       vr=VR,
                       offset=offset,
                       value=value,
                       name=name,
                       bytelen=length)
        return tag

class Pdcm(dict):
    """Parsed dicom file.
    """

    def __init__(self, filename):
        """DICOM object"""

        self.filename = filename

        self.parse()

    def imshow(self):
        """Display the image data.
        """

        # The method is pretty simple, just write out a temporary file and 
        # hope that PIL can handle it.
        if self['TransferSyntaxUID'].value == '1.2.840.10008.1.2.1':
            # Cast the data.
            image = np.frombuffer(self['PixelData'].value, dtype=np.uint16)
            #np.reshape(image, (self['Rows'].value, self['Columns'].value))
            image.shape = (self['Rows'].value, self['Columns'].value)
            matplotlib.pyplot.imshow(image)
            return
        elif self['TransferSyntaxUID'].value == '1.2.840.10008.1.2.4.91':
            with tempfile.NamedTemporaryFile(delete=False) as tfile:
                tfile.write(self['PixelData'].value)
                tfile.flush()
                matplotlib.pyplot.imshow(tfile.name)

        else:
            msg = "Transfer syntax UID {0} not yet supported."
            raise RuntimeError(msg.format(self['TransferSyntaxUID'].value))

    def parse(self):
        """Parse the entire DICOM file.
        """
        with open(self.filename, 'rb') as fptr:
            # Scan past the 128-byte preamble.
            fptr.seek(128)

            read_buffer = fptr.read(4)
            data, = struct.unpack('>4s', read_buffer)
            self.__setitem__('dicom prefix',  data)

            moredata = True
            while moredata:
                tag = DicomTag.parse(fptr)
                #print(tag)
                self.__setitem__(tag.name, tag)
                if fptr.tell() == os.path.getsize(self.filename):
                    moredata = False



if __name__ == "__main__":
    FILENAME = '/opt/data/dicom//WRIX/WRIX/WRIST RIGHT/SCOUT 3-PLANE RT. - 2/IM-0001-0001.dcm'
    FILENAME = '/opt/data/dicom/LIDC-IDRI/LIDC-IDRI-0046/1.3.6.1.4.1.14519.5.2.1.6279.6001.189975013581257814721620649088/000000/000001.dcm'
    FILENAME = '/opt/data/dicom/matlab/examples/sample_data/DICOM/digest_article/brain_018.dcm'
    FILENAME = '/opt/data/dicom/LIDC-IDRI/LIDC-IDRI-0046/1.3.6.1.4.1.14519.5.2.1.6279.6001.189975013581257814721620649088/000000/000000.dcm'
    obj = Pdcm(FILENAME)
    obj.imshow()
    matplotlib.pyplot.show()
