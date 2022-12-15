import React from 'react';
import { Outlet } from 'react-router-dom';
import { Grid } from '@mui/material';
import Menu from '../../components/menu';

const ProfileLayout = ({ auth }) => (
  <Grid
    container
    justifyContent="flex-start"
    alignItems="flex-start"
    sx={{ height: '100%' }}
  >
    <Grid
      item
      md={2.5}
      sm={1}
      sx={{
        justifyContent: 'center', display: 'flex', borderRight: '1px solid #DCDCDC',
      }}
    >
      <Menu auth={auth} />
    </Grid>

    <Grid item md sm={1} container sx={{ height: '100%' }}>
      <Outlet />
    </Grid>
  </Grid>
);

export default ProfileLayout;
