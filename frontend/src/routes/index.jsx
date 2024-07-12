import Analysis from '../pages/Analysis'
import ReportDetails from '../pages/ReportDetails'
import Home from '../pages/Home'
import PageNotFound from '../pages/PageNotFound'

const appRoutes = [
	{
		path: '/',
		element: <Home />,
	},
	{
		path: '/report/:reportID',
		element: <ReportDetails />,
	},
	{
		path: '/analytics',
		element: <Analysis />,
	},
	{
		path: '*',
		element: <PageNotFound />,
	},
]

export default appRoutes
