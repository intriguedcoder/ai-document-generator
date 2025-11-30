import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import {
  Box, Flex, Button, Heading, HStack, Avatar, Menu,
  MenuButton, MenuList, MenuItem, MenuDivider
} from '@chakra-ui/react';
import { ChevronDownIcon } from '@chakra-ui/icons';

export const Navbar = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <Box bg="blue.600" px={8} py={4} color="white" shadow="md">
      <Flex justify="space-between" align="center">
        <Heading
          size="md"
          cursor="pointer"
          onClick={() => navigate('/dashboard')}
        >
          AI Document Generator
        </Heading>
        
        {user && (
          <HStack spacing={4}>
            <Button
              variant="ghost"
              color="white"
              onClick={() => navigate('/dashboard')}
              _hover={{ bg: 'blue.700' }}
            >
              My Projects
            </Button>
            
            <Menu>
              <MenuButton as={Button} rightIcon={<ChevronDownIcon />} variant="ghost" color="white">
                <HStack>
                  <Avatar size="sm" name="User" />
                </HStack>
              </MenuButton>
              <MenuList color="black">
                <MenuItem onClick={() => navigate('/dashboard')}>Dashboard</MenuItem>
                <MenuDivider />
                <MenuItem onClick={handleLogout}>Logout</MenuItem>
              </MenuList>
            </Menu>
          </HStack>
        )}
      </Flex>
    </Box>
  );
};
