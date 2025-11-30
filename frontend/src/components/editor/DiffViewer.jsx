import { Box, Text, Heading } from '@chakra-ui/react';
import { diffWords } from 'diff';

export const DiffViewer = ({ original, refined }) => {
  if (!original || !refined) return null;

  const diff = diffWords(original, refined);

  return (
    <Box p={4} bg="gray.50" borderWidth={1} borderRadius="md">
      <Heading size="sm" mb={3} color="gray.700">
        Changes Made:
      </Heading>
      <Box>
        {diff.map((part, i) => (
          <Text
            as="span"
            key={i}
            bg={
              part.added
                ? 'green.100'
                : part.removed
                ? 'red.100'
                : 'transparent'
            }
            textDecoration={part.removed ? 'line-through' : 'none'}
            color={
              part.added
                ? 'green.800'
                : part.removed
                ? 'red.800'
                : 'gray.800'
            }
            px={part.added || part.removed ? 1 : 0}
          >
            {part.value}
          </Text>
        ))}
      </Box>
    </Box>
  );
};
