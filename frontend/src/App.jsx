import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ChakraProvider, Box, Flex } from '@chakra-ui/react';
import { AuthProvider } from './context/AuthContext';
import { ProtectedRoute } from './components/auth/ProtectedRoute';
import { Navbar } from './components/common/Navbar';
import { Login } from './components/auth/Login';
import { Register } from './components/auth/Register';
import { ProjectList } from './components/dashboard/ProjectList';
import { ProjectConfig } from './components/configuration/ProjectConfig';
import { DocumentEditor } from './components/editor/DocumentEditor';

function App() {
  return (
    <ChakraProvider>
      <AuthProvider>
        <BrowserRouter>
          {/* full-screen dark background */}
          <Box minH="100vh" bg="gray.900">
            <Routes>
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />

              <Route
                path="/dashboard"
                element={
                  <ProtectedRoute>
                    <>
                      <Navbar />
                      {/* centered panel */}
                      <Flex justify="center" px={4} py={6}>
                        <Box w="100%" maxW="1200px" bg="gray.900">
                          <ProjectList />
                        </Box>
                      </Flex>
                    </>
                  </ProtectedRoute>
                }
              />

              <Route
                path="/create"
                element={
                  <ProtectedRoute>
                    <>
                      <Navbar />
                      <Flex justify="center" px={4} py={6}>
                        <Box w="100%" maxW="1200px" bg="gray.900">
                          <ProjectConfig />
                        </Box>
                      </Flex>
                    </>
                  </ProtectedRoute>
                }
              />

              <Route
                path="/editor/:projectId"
                element={
                  <ProtectedRoute>
                    <>
                      <Navbar />
                      <Flex justify="center" px={4} py={6}>
                        <Box w="100%" maxW="1200px" bg="gray.900">
                          <DocumentEditor />
                        </Box>
                      </Flex>
                    </>
                  </ProtectedRoute>
                }
              />
            </Routes>
          </Box>
        </BrowserRouter>
      </AuthProvider>
    </ChakraProvider>
  );
}

export default App;
