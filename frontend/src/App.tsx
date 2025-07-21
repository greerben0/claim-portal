
import TopNavigation from "@cloudscape-design/components/top-navigation";
import SpaceBetween from "@cloudscape-design/components/space-between";

import react_svg from './assets/react.svg';
import ClaimTable from './components/ClaimTable';
import ClaimForm from './components/ClaimForm';
import type { ClaimItem } from "./types"


import { useEffect, useState } from 'react';
import { getClaims } from './utils/api';

import { Authenticator } from '@aws-amplify/ui-react';
import { Amplify } from 'aws-amplify';
import '@aws-amplify/ui-react/styles.css';
import { fetchAuthSession } from '@aws-amplify/auth';

const userPoolId = import.meta.env.VITE_USER_POOL_ID
const userPoolClientId = import.meta.env.VITE_USER_POOL_CLIENT_ID

Amplify.configure({
  Auth: {
    Cognito: {
      userPoolId: userPoolId,
      userPoolClientId: userPoolClientId,
      identityPoolId: "",
      loginWith: {
        email: true,
      },
      signUpVerificationMethod: "code",
      userAttributes: {
        email: {
          required: true,
        },
      },
      allowGuestAccess: true,
      passwordFormat: {
        minLength: 8,
        requireLowercase: true,
        requireUppercase: true,
        requireNumbers: true,
        requireSpecialCharacters: true,
      },
    },
  },
})

const App = () => {
  const [claims, setClaims] = useState<ClaimItem[]>([]);
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    refreshClaims()
  }, [])

  const refreshClaims = () => {
    setLoading(true)
    fetchAuthSession()
      .then((session) => {
        const accessToken = session.tokens?.accessToken?.toString()
        getClaims(accessToken || '')
          .then((r) => r.json())
          .then((r) => setClaims(r.claims))
          .then(() => setLoading(false))
      }).catch((e) => {
        console.error(e)
        setLoading(false)
      })
  }

  return (
    <Authenticator>
      {({ signOut =  () => {}, user }) => (
        <>
          <TopNavigation
            identity={{
              href: '#',
              title: 'Claim Portal',
              logo: {
                src: react_svg,
                alt: 'Logo',
              },
            }}

            utilities={[
              {
                type: 'button',
                text: user?.username || '',
              },
              {
                type: 'button',
                text: 'Sign out',
                onClick: () => { signOut() },
              },
            ]}
          />
          <SpaceBetween direction="vertical" size="xl">
            <ClaimForm submitHandler={refreshClaims} />
            <ClaimTable claims={claims} loading={loading} triggerRefresh={refreshClaims} />
          </SpaceBetween>
        </>
      )}
    </Authenticator>
  )
}

export default App
