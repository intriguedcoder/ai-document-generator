import {
  Box, Button, VStack, Text, Badge, HStack, Divider,
  useDisclosure, Modal, ModalOverlay, ModalContent,
  ModalHeader, ModalBody, ModalCloseButton, ModalFooter
} from '@chakra-ui/react';
import { format } from 'date-fns';

export const VersionHistory = ({ versions, onRevert }) => {
  const { isOpen, onOpen, onClose } = useDisclosure();

  if (!versions || versions.length === 0) {
    return (
      <Text fontSize="sm" color="gray.500">
        No version history yet
      </Text>
    );
  }

  return (
    <>
      <Button size="sm" onClick={onOpen} variant="outline">
        View History ({versions.length} versions)
      </Button>

      <Modal isOpen={isOpen} onClose={onClose} size="xl" scrollBehavior="inside">
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>Version History</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <VStack spacing={4} align="stretch">
              {versions.map((version, index) => (
                <Box
                  key={index}
                  p={4}
                  borderWidth={1}
                  borderRadius="md"
                  bg={index === versions.length - 1 ? 'blue.50' : 'white'}
                >
                  <HStack justify="space-between" mb={2}>
                    <HStack>
                      <Badge colorScheme="blue">Version {version.version}</Badge>
                      {index === versions.length - 1 && (
                        <Badge colorScheme="green">Current</Badge>
                      )}
                    </HStack>
                    <Text fontSize="xs" color="gray.500">
                      {format(new Date(version.timestamp), 'MMM d, yyyy HH:mm')}
                    </Text>
                  </HStack>

                  {version.prompt && (
                    <Text fontSize="sm" color="gray.600" mb={2}>
                      <strong>Prompt:</strong> {version.prompt}
                    </Text>
                  )}

                  {version.feedback && (
                    <Badge
                      colorScheme={version.feedback === 'like' ? 'green' : 'red'}
                      mb={2}
                    >
                      {version.feedback === 'like' ? '👍 Liked' : '👎 Disliked'}
                    </Badge>
                  )}

                  {version.comment && (
                    <Text fontSize="sm" color="gray.600" fontStyle="italic">
                      "{version.comment}"
                    </Text>
                  )}

                  {index !== versions.length - 1 && (
                    <Button
                      size="xs"
                      colorScheme="blue"
                      variant="outline"
                      mt={2}
                      onClick={() => {
                        onRevert(version.version);
                        onClose();
                      }}
                    >
                      Revert to this version
                    </Button>
                  )}

                  <Divider mt={3} />
                  <Text fontSize="sm" color="gray.700" mt={3} noOfLines={3}>
                    {version.content}
                  </Text>
                </Box>
              ))}
            </VStack>
          </ModalBody>
          <ModalFooter>
            <Button onClick={onClose}>Close</Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </>
  );
};
