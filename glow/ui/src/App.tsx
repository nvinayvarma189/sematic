import AppBar from "@mui/material/AppBar";
import Typography from "@mui/material/Typography";
import LightModeIcon from "@mui/icons-material/LightMode";
import Toolbar from "@mui/material/Toolbar";
import Container from "@mui/material/Container";
import Button from "@mui/material/Button";
import Box from "@mui/system/Box";
import { Outlet } from "react-router-dom";
import Link from "@mui/material/Link";
import { ThemeProvider as MuiThemeProvider } from "@mui/material/styles";
import createTheme from "./themes/mira";

const pages = [
  ["Pipelines", "/pipelines"],
  ["Runs", "/runs"],
  ["Docs", "/"],
];

function App() {
  return (
    <>
      <MuiThemeProvider theme={createTheme("LIGHT")}>
        <AppBar position="static" color="transparent" sx={{ boxShadow: 0 }}>
          <Container maxWidth="xl">
            <Toolbar>
              <LightModeIcon color="primary" />
              <Link href="/" sx={{ color: "white" }} underline="none">
                <Typography
                  variant="h5"
                  component="h1"
                  color="primary"
                  sx={{
                    marginRight: 2,
                    marginLeft: 1,
                  }}
                >
                  Glow
                </Typography>
              </Link>
              <Box sx={{ flexGrow: 1, display: "flex" }}>
                {pages.map((page) => (
                  <Button
                    key={page[0]}
                    sx={{
                      marginY: 2,
                      marginLeft: 7,
                      //color: "white",
                      display: "block",
                    }}
                    href={page[1]}
                  >
                    {page[0]}
                  </Button>
                ))}
              </Box>
            </Toolbar>
          </Container>
        </AppBar>
        <Container maxWidth="lg" sx={{ paddingTop: 4 }}>
          <Container maxWidth="xl">
            <Outlet />
          </Container>
        </Container>
      </MuiThemeProvider>
    </>
  );
}

export default App;